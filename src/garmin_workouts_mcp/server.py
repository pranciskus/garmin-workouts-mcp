from __future__ import annotations

import logging
import os
import sys
from threading import Lock
from datetime import datetime

import garth
from fastmcp import FastMCP

from .payloads import (
    WorkoutInput,
    build_workout_payload,
    describe_workout,
    list_strength_exercise_aliases,
    resolve_strength_exercise,
)


LIST_WORKOUTS_ENDPOINT = "/workout-service/workouts"
GET_WORKOUT_ENDPOINT = "/workout-service/workout/{workout_id}"
GET_ACTIVITY_ENDPOINT = "/activity-service/activity/{activity_id}"
GET_ACTIVITY_WEATHER_ENDPOINT = "/activity-service/activity/{activity_id}/weather"
LIST_ACTIVITIES_ENDPOINT = "/activitylist-service/activities/search/activities"
CREATE_WORKOUT_ENDPOINT = "/workout-service/workout"
SCHEDULE_WORKOUT_ENDPOINT = "/workout-service/schedule/{workout_id}"
CALENDAR_WEEK_ENDPOINT = "/calendar-service/year/{year}/month/{month}/day/{day}/start/{start}"
CALENDAR_MONTH_ENDPOINT = "/calendar-service/year/{year}/month/{month}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="GarminWorkoutsMCP")
_AUTH_LOCK = Lock()
_AUTH_READY = False


def _ensure_authenticated() -> None:
    global _AUTH_READY

    if _AUTH_READY:
        return

    with _AUTH_LOCK:
        if _AUTH_READY:
            return

        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")
        garth_home = os.environ.get("GARTH_HOME")

        if email or password:
            if not (email and password):
                raise RuntimeError(
                    "Garmin credentials are incomplete. Set both GARMIN_EMAIL and GARMIN_PASSWORD."
                )
            try:
                garth.login(email, password)
            except Exception as exc:
                raise RuntimeError(
                    "Failed to authenticate with Garmin using GARMIN_EMAIL and GARMIN_PASSWORD."
                ) from exc

            if garth_home:
                try:
                    garth.save(garth_home)
                except Exception as exc:
                    logger.warning("Authenticated with Garmin but failed to save tokens to GARTH_HOME: %s", exc)

            _AUTH_READY = True
            return

        if garth_home:
            try:
                garth.resume(garth_home)
            except Exception as exc:
                raise RuntimeError(
                    "Failed to resume Garmin session from GARTH_HOME."
                ) from exc
            _AUTH_READY = True
            return

        raise RuntimeError(
            "Garmin credentials are required for this tool. Set GARMIN_EMAIL and GARMIN_PASSWORD, "
            "or set GARTH_HOME to a directory containing saved Garmin tokens."
        )


def _connectapi(endpoint: str, method: str = "GET", **kwargs) -> dict:
    _ensure_authenticated()
    return garth.connectapi(endpoint, method=method, **kwargs)


@mcp.tool
def list_workouts() -> dict:
    workouts = _connectapi(LIST_WORKOUTS_ENDPOINT)
    return {"workouts": workouts}


@mcp.tool
def get_workout(workout_id: str) -> dict:
    endpoint = GET_WORKOUT_ENDPOINT.format(workout_id=workout_id)
    return {"workout": _connectapi(endpoint)}


@mcp.tool
def delete_workout(workout_id: str) -> bool:
    endpoint = GET_WORKOUT_ENDPOINT.format(workout_id=workout_id)
    try:
        _connectapi(endpoint, method="DELETE")
        logger.info("Deleted workout %s", workout_id)
        return True
    except Exception as exc:
        logger.error("Failed deleting workout %s: %s", workout_id, exc)
        return False


@mcp.tool
def upload_workout(workout_data: dict) -> dict:
    payload = build_workout_payload(workout_data)
    result = _connectapi(CREATE_WORKOUT_ENDPOINT, method="POST", json=payload)
    workout_id = result.get("workoutId")
    if workout_id is None:
        raise ValueError(f"Garmin did not return workoutId: {result}")
    return {"workoutId": str(workout_id), "payloadPreview": payload}


@mcp.tool
def preview_workout_payload(workout_data: dict) -> dict:
    return {"payload": build_workout_payload(workout_data)}


@mcp.tool
def validate_workout(workout_data: dict) -> dict:
    summary = describe_workout(workout_data)
    return {"valid": True, "summary": summary}


@mcp.tool
def list_supported_strength_exercises(query: str | None = None) -> dict:
    return {"exercises": list_strength_exercise_aliases(query)}


@mcp.tool
def resolve_supported_strength_exercise(query: str) -> dict:
    return resolve_strength_exercise(query)


@mcp.tool
def get_workout_input_schema() -> dict:
    return {"schema": WorkoutInput.model_json_schema()}


@mcp.tool
def schedule_workout(workout_id: str, date: str) -> dict:
    datetime.strptime(date, "%Y-%m-%d")
    endpoint = SCHEDULE_WORKOUT_ENDPOINT.format(workout_id=workout_id)
    result = _connectapi(endpoint, method="POST", json={"date": date})
    workout_schedule_id = result.get("workoutScheduleId")
    if workout_schedule_id is None:
        raise ValueError(f"Scheduling failed: {result}")
    return {"workoutScheduleId": str(workout_schedule_id)}


@mcp.tool
def get_activity(activity_id: str) -> dict:
    endpoint = GET_ACTIVITY_ENDPOINT.format(activity_id=activity_id)
    return _connectapi(endpoint)


@mcp.tool
def get_activity_weather(activity_id: str) -> dict:
    endpoint = GET_ACTIVITY_WEATHER_ENDPOINT.format(activity_id=activity_id)
    return _connectapi(endpoint)


@mcp.tool
def list_activities(limit: int = 20, start: int = 0, activityType: str | None = None, search: str | None = None) -> dict:
    params = {"limit": limit, "start": start}
    if activityType is not None:
        params["activityType"] = activityType
    if search is not None:
        params["search"] = search
    return {"activities": _connectapi(LIST_ACTIVITIES_ENDPOINT, params=params)}


@mcp.tool
def get_calendar(year: int, month: int, day: int | None = None, start: int = 1) -> dict:
    if not 1900 <= year <= 2100:
        raise ValueError(f"Year must be between 1900 and 2100, got {year}")
    if not 1 <= month <= 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")
    if day is not None and not 1 <= day <= 31:
        raise ValueError(f"Day must be between 1 and 31, got {day}")

    garmin_month = month - 1
    if day is None:
        endpoint = CALENDAR_MONTH_ENDPOINT.format(year=year, month=garmin_month)
        view_type = "month"
    else:
        endpoint = CALENDAR_WEEK_ENDPOINT.format(year=year, month=garmin_month, day=day, start=start)
        view_type = "week"

    return {
        "calendar": _connectapi(endpoint),
        "view_type": view_type,
        "period": {"year": year, "month": month, "day": day, "start": start if day else None},
    }


@mcp.tool
def generate_workout_data_prompt(description: str) -> dict:
    return {
        "prompt": f"""
You are producing JSON for the Garmin Workouts MCP server.

Workout description:
{description}

Return valid JSON only.

Top-level shape:
{{
  "name": "Workout name",
  "type": "running" | "cycling" | "walking" | "swimming" | "cardio" | "strength",
  "description": "Optional workout description",
  "steps": [...]
}}

Executable step shape:
{{
  "stepType": "warmup" | "cooldown" | "interval" | "recovery" | "rest",
  "stepDescription": "Optional note",
  "endConditionType": "time" | "distance" | "lap.button" | "reps",
  "stepDuration": 300,
  "stepDistance": 1000,
  "distanceUnit": "m" | "km" | "mile",
  "stepReps": 8,
  "target": {{
    "type": "no target" | "pace" | "heart rate" | "power" | "cadence" | "speed",
    "value": null | 160 | [150, 170],
    "unit": null | "min_per_km" | "bpm" | "watts"
  }},
  "exercise": "friendly alias"
}}

Strength exercises can also use explicit Garmin enums:
{{
  "exercise": {{
    "category": "BENCH_PRESS",
    "exerciseName": "INCLINE_DUMBBELL_BENCH_PRESS"
  }}
}}

Repeat group shape:
{{
  "stepType": "repeat",
  "endConditionType": "repeat",
  "numberOfIterations": 3,
  "steps": [ ... child executable steps ... ]
}}

Rules:
- Time steps use stepDuration in seconds.
- Distance steps use stepDistance plus distanceUnit.
- Rep steps use stepReps and should include exercise for strength workouts.
- Lap-button note steps do not need duration.
- Return JSON only, with no markdown fences.
"""
    }
