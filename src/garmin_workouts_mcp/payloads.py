from __future__ import annotations

import difflib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


SPORT_TYPE_MAPPING = {
    "running": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
    "cycling": {"sportTypeId": 2, "sportTypeKey": "cycling", "displayOrder": 2},
    "walking": {"sportTypeId": 3, "sportTypeKey": "walking", "displayOrder": 3},
    "swimming": {"sportTypeId": 4, "sportTypeKey": "swimming", "displayOrder": 5},
    "strength": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 5},
    "cardio": {"sportTypeId": 6, "sportTypeKey": "cardio_training", "displayOrder": 8},
}

STEP_TYPE_MAPPING = {
    "warmup": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
    "cooldown": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
    "interval": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
    "recovery": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
    "rest": {"stepTypeId": 5, "stepTypeKey": "rest", "displayOrder": 5},
    "repeat": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
}

TARGET_TYPE_MAPPING = {
    "no target": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1},
    "power": {"workoutTargetTypeId": 2, "workoutTargetTypeKey": "power.zone", "displayOrder": 2},
    "cadence": {"workoutTargetTypeId": 3, "workoutTargetTypeKey": "cadence.zone", "displayOrder": 3},
    "heart rate": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    "speed": {"workoutTargetTypeId": 5, "workoutTargetTypeKey": "speed.zone", "displayOrder": 5},
    "pace": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
}

DISTANCE_UNIT_MAPPING = {
    "m": {"unitId": 2, "unitKey": "m", "factor": 1.0},
    "km": {"unitId": 3, "unitKey": "km", "factor": 1000.0},
    "mile": {"unitId": 4, "unitKey": "mile", "factor": 1609.344},
}

END_CONDITION_TYPE_MAPPING = {
    "lap.button": {"conditionTypeId": 1, "conditionTypeKey": "lap.button", "displayOrder": 1, "displayable": True},
    "time": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
    "distance": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
    "iterations": {"conditionTypeId": 7, "conditionTypeKey": "iterations", "displayOrder": 7, "displayable": False},
    "reps": {"conditionTypeId": 10, "conditionTypeKey": "reps", "displayOrder": 10, "displayable": True},
}


EXERCISE_ALIAS_MAP = {
    "bench press": {"category": "BENCH_PRESS", "exerciseName": "BENCH_PRESS"},
    "flat db press": {"category": "BENCH_PRESS", "exerciseName": "DUMBBELL_BENCH_PRESS"},
    "dumbbell bench press": {"category": "BENCH_PRESS", "exerciseName": "DUMBBELL_BENCH_PRESS"},
    "incline db press": {"category": "BENCH_PRESS", "exerciseName": "INCLINE_DUMBBELL_BENCH_PRESS"},
    "incline dumbbell bench press": {"category": "BENCH_PRESS", "exerciseName": "INCLINE_DUMBBELL_BENCH_PRESS"},
    "hack squat": {"category": "SQUAT", "exerciseName": "BARBELL_HACK_SQUAT"},
    "leg press": {"category": "SQUAT", "exerciseName": "LEG_PRESS"},
    "romanian deadlift": {"category": "DEADLIFT", "exerciseName": "BARBELL_STRAIGHT_LEG_DEADLIFT"},
    "rdl": {"category": "DEADLIFT", "exerciseName": "BARBELL_STRAIGHT_LEG_DEADLIFT"},
    "seated hamstring curl": {"category": "LEG_CURL", "exerciseName": "LEG_CURL"},
    "leg curl": {"category": "LEG_CURL", "exerciseName": "LEG_CURL"},
    "leg extension": {"category": "CRUNCH", "exerciseName": "LEG_EXTENSIONS"},
    "leg extensions": {"category": "CRUNCH", "exerciseName": "LEG_EXTENSIONS"},
    "t bar row": {"category": "ROW", "exerciseName": "T_BAR_ROW"},
    "seated cable row": {"category": "ROW", "exerciseName": "SEATED_CABLE_ROW"},
    "row": {"category": "ROW", "exerciseName": "ROW"},
    "lat pulldown": {"category": "PULL_UP", "exerciseName": "LAT_PULLDOWN"},
    "wide grip lat pulldown": {"category": "PULL_UP", "exerciseName": "WIDE_GRIP_LAT_PULLDOWN"},
    "pull up": {"category": "PULL_UP", "exerciseName": "PULL_UP"},
    "seated db shoulder press": {"category": "SHOULDER_PRESS", "exerciseName": "SEATED_DUMBBELL_SHOULDER_PRESS"},
    "shoulder press": {"category": "SHOULDER_PRESS", "exerciseName": "SHOULDER_PRESS"},
    "ez bar skull crusher": {"category": "TRICEPS_EXTENSION", "exerciseName": "LYING_EZ_BAR_TRICEPS_EXTENSION"},
    "skull crusher": {"category": "TRICEPS_EXTENSION", "exerciseName": "LYING_EZ_BAR_TRICEPS_EXTENSION"},
    "ez bar curl": {"category": "CURL", "exerciseName": "STANDING_EZ_BAR_BICEPS_CURL"},
    "db bicep curl": {"category": "CURL", "exerciseName": "STANDING_ALTERNATING_DUMBBELL_CURLS"},
    "dumbbell curl": {"category": "CURL", "exerciseName": "STANDING_ALTERNATING_DUMBBELL_CURLS"},
    "db lateral raise": {"category": "LATERAL_RAISE", "exerciseName": "LEANING_DUMBBELL_LATERAL_RAISE"},
    "dumbbell lateral raise": {"category": "LATERAL_RAISE", "exerciseName": "LEANING_DUMBBELL_LATERAL_RAISE"},
    "seated calf raise": {"category": "CALF_RAISE", "exerciseName": "SEATED_CALF_RAISE"},
    "cable crunch": {"category": "CRUNCH", "exerciseName": "KNEELING_CABLE_CRUNCH"},
    "crunch": {"category": "CRUNCH", "exerciseName": "CRUNCH"},
}


class TargetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = "no target"
    value: float | list[float] | None = None
    unit: str | None = None


class ExerciseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lookup: str | None = None
    category: str | None = None
    exerciseName: str | None = None


class StepInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    stepName: str | None = None
    stepDescription: str | None = None
    stepType: str | None = None
    endConditionType: str | None = None
    stepDuration: float | None = None
    stepDistance: float | None = None
    distanceUnit: str | None = None
    stepReps: float | None = None
    numberOfIterations: int | None = None
    steps: list["StepInput"] | None = None
    target: TargetInput | None = None
    exercise: str | ExerciseInput | None = None
    category: str | None = None
    exerciseName: str | None = None
    weightValue: float | None = None
    weightUnit: str | None = None


class WorkoutInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    type: str
    description: str | None = None
    steps: list[StepInput] = Field(min_length=1)


StepInput.model_rebuild()


def validate_workout_input(workout: dict[str, Any]) -> WorkoutInput:
    try:
        return WorkoutInput.model_validate(workout)
    except ValidationError as exc:
        raise ValueError(exc.json()) from exc


def build_workout_payload(workout: dict[str, Any]) -> dict[str, Any]:
    parsed = validate_workout_input(workout)
    sport_type_key = parsed.type.lower()
    sport_type = _get_sport_type(sport_type_key)
    steps, next_order = _process_steps(parsed.steps, sport_type_key, 1)
    payload = {
        "sportType": sport_type,
        "subSportType": None,
        "workoutName": parsed.name,
        "description": parsed.description,
        "estimatedDistanceUnit": {"unitKey": None},
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": sport_type,
                "workoutSteps": steps,
            }
        ],
        "avgTrainingSpeed": None,
        "estimatedDurationInSecs": _estimate_duration(steps),
        "estimatedDistanceInMeters": _estimate_distance(steps),
        "estimateType": None,
    }
    if next_order <= 1:
        raise ValueError("Workout must contain at least one step")
    return payload


def describe_workout(workout: dict[str, Any]) -> dict[str, Any]:
    payload = build_workout_payload(workout)
    steps = payload["workoutSegments"][0]["workoutSteps"]
    executable_steps = [step for step in steps if step["type"] == "ExecutableStepDTO"]
    rep_steps = [step for step in executable_steps if step["endCondition"]["conditionTypeKey"] == "reps"]
    strength_steps = [step for step in executable_steps if step.get("exerciseName")]
    return {
        "name": payload["workoutName"],
        "sportType": payload["sportType"]["sportTypeKey"],
        "stepCount": len(steps),
        "executableStepCount": len(executable_steps),
        "repStepCount": len(rep_steps),
        "mappedStrengthExerciseCount": len(strength_steps),
        "estimatedDurationInSecs": payload["estimatedDurationInSecs"],
        "estimatedDistanceInMeters": payload["estimatedDistanceInMeters"],
    }


def list_strength_exercise_aliases(query: str | None = None) -> dict[str, dict[str, str]]:
    if not query:
        return dict(sorted(EXERCISE_ALIAS_MAP.items()))
    needle = _normalize_text(query)
    return {
        alias: mapping
        for alias, mapping in sorted(EXERCISE_ALIAS_MAP.items())
        if needle in _normalize_text(alias)
        or needle in mapping["category"].lower()
        or needle in mapping["exerciseName"].lower()
    }


def resolve_strength_exercise(value: str) -> dict[str, Any]:
    normalized = _normalize_text(value)
    direct = EXERCISE_ALIAS_MAP.get(normalized)
    if direct:
        return {
            "query": value,
            "normalizedQuery": normalized,
            "matched": True,
            "mapping": direct,
            "suggestions": [],
        }
    suggestions = difflib.get_close_matches(normalized, EXERCISE_ALIAS_MAP.keys(), n=5, cutoff=0.5)
    return {
        "query": value,
        "normalizedQuery": normalized,
        "matched": False,
        "mapping": None,
        "suggestions": [
            {"alias": alias, "mapping": EXERCISE_ALIAS_MAP[alias]}
            for alias in suggestions
        ],
    }


def _process_steps(steps: list[StepInput], sport_type_key: str, step_order: int) -> tuple[list[dict[str, Any]], int]:
    payload_steps: list[dict[str, Any]] = []
    for step in steps:
        payload_step, step_order = _process_step(step, sport_type_key, step_order)
        payload_steps.append(payload_step)
    return payload_steps, step_order


def _process_step(step: StepInput, sport_type_key: str, step_order: int) -> tuple[dict[str, Any], int]:
    step_type = (step.stepType or "").lower()
    end_condition_type = (step.endConditionType or "").lower()
    if (
        step.numberOfIterations
        and step.steps
        and (step_type == "repeat" or end_condition_type == "repeat")
    ):
        return _build_repeat_step(step, sport_type_key, step_order)
    return _build_executable_step(step, sport_type_key, step_order)


def _build_repeat_step(step: StepInput, sport_type_key: str, step_order: int) -> tuple[dict[str, Any], int]:
    if not step.steps:
        raise ValueError("Repeat steps must include child steps")
    if not step.numberOfIterations or step.numberOfIterations <= 0:
        raise ValueError("Repeat steps must include a positive numberOfIterations")
    child_steps, next_order = _process_steps(step.steps, sport_type_key, step_order + 1)
    return {
        "stepId": step_order,
        "stepOrder": step_order,
        "stepType": STEP_TYPE_MAPPING["repeat"],
        "numberOfIterations": step.numberOfIterations,
        "smartRepeat": False,
        "endCondition": END_CONDITION_TYPE_MAPPING["iterations"],
        "type": "RepeatGroupDTO",
        "workoutSteps": child_steps,
    }, next_order


def _build_executable_step(step: StepInput, sport_type_key: str, step_order: int) -> tuple[dict[str, Any], int]:
    step_type_key = (step.stepType or "interval").lower()
    if step_type_key not in STEP_TYPE_MAPPING:
        raise ValueError(f"Unsupported stepType: {step.stepType}")
    payload_step: dict[str, Any] = {
        "stepId": step_order,
        "stepOrder": step_order,
        "stepType": STEP_TYPE_MAPPING[step_type_key],
        "type": "ExecutableStepDTO",
        "description": step.stepDescription or "",
        "stepAudioNote": None,
        "targetType": TARGET_TYPE_MAPPING["no target"],
    }

    end_condition_key, end_condition_value = _resolve_end_condition(step)
    payload_step["endCondition"] = END_CONDITION_TYPE_MAPPING[end_condition_key]
    if end_condition_value is not None:
        payload_step["endConditionValue"] = end_condition_value

    if step.target:
        _apply_target(payload_step, step.target)

    exercise_ref = _resolve_exercise(step)
    needs_exercise = sport_type_key == "strength" and (
        end_condition_key == "reps" or exercise_ref is not None
    )
    if needs_exercise and exercise_ref is None:
        raise ValueError(
            f"Strength step {step_order} is missing exercise mapping. "
            "Pass step.exercise as a friendly alias or explicit category/exerciseName."
        )
    if exercise_ref:
        payload_step["category"] = exercise_ref["category"]
        payload_step["exerciseName"] = exercise_ref["exerciseName"]

    if step.weightValue is not None:
        payload_step["weightValue"] = step.weightValue
        payload_step["weightUnit"] = step.weightUnit

    return payload_step, step_order + 1


def _resolve_end_condition(step: StepInput) -> tuple[str, float | None]:
    key = (step.endConditionType or "").lower()
    if not key:
        if step.stepDuration is not None:
            key = "time"
        elif step.stepDistance is not None:
            key = "distance"
        elif step.stepReps is not None:
            key = "reps"
        else:
            raise ValueError("Step is missing endConditionType")
    if key == "time":
        if step.stepDuration is None or step.stepDuration <= 0:
            raise ValueError("Time steps must include a positive stepDuration")
        return key, float(step.stepDuration)
    if key == "distance":
        if step.stepDistance is None or step.stepDistance <= 0:
            raise ValueError("Distance steps must include a positive stepDistance")
        if not step.distanceUnit:
            raise ValueError("Distance steps must include distanceUnit")
        unit = DISTANCE_UNIT_MAPPING.get(step.distanceUnit.lower())
        if not unit:
            raise ValueError(f"Unsupported distanceUnit: {step.distanceUnit}")
        return key, float(step.stepDistance) * unit["factor"]
    if key == "reps":
        if step.stepReps is None or step.stepReps <= 0:
            raise ValueError("Rep steps must include a positive stepReps")
        return key, float(step.stepReps)
    if key == "lap.button":
        return key, None
    raise ValueError(f"Unsupported endConditionType: {step.endConditionType}")


def _apply_target(payload_step: dict[str, Any], target: TargetInput) -> None:
    target_key = target.type.lower()
    if target_key not in TARGET_TYPE_MAPPING:
        raise ValueError(f"Unsupported target type: {target.type}")
    payload_step["targetType"] = TARGET_TYPE_MAPPING[target_key]
    if target_key == "no target" or target.value is None:
        return
    if isinstance(target.value, list):
        if len(target.value) != 2:
            raise ValueError("Target value lists must contain exactly two items")
        low, high = float(target.value[0]), float(target.value[1])
    else:
        low, high = float(target.value), float(target.value)
    if target_key == "pace":
        low, high = _convert_pace_range(low, high, target.unit)
    else:
        if low > high:
            low, high = high, low
    payload_step["targetValueOne"] = low
    payload_step["targetValueTwo"] = high
    payload_step["targetValueUnit"] = None


def _convert_pace_range(low: float, high: float, unit: str | None) -> tuple[float, float]:
    pace_unit = (unit or "min_per_km").lower()
    if pace_unit != "min_per_km":
        raise ValueError(f"Unsupported pace unit: {unit}")
    fast = 1000.0 / (low * 60.0)
    slow = 1000.0 / (high * 60.0)
    if fast < slow:
        fast, slow = slow, fast
    return fast, slow


def _resolve_exercise(step: StepInput) -> dict[str, str] | None:
    if step.category and step.exerciseName:
        return {"category": step.category, "exerciseName": step.exerciseName}
    if isinstance(step.exercise, str):
        return _resolve_exercise_alias(step.exercise)
    if isinstance(step.exercise, ExerciseInput):
        if step.exercise.category and step.exercise.exerciseName:
            return {
                "category": step.exercise.category,
                "exerciseName": step.exercise.exerciseName,
            }
        if step.exercise.lookup:
            return _resolve_exercise_alias(step.exercise.lookup)
    return None


def _resolve_exercise_alias(alias: str) -> dict[str, str]:
    normalized = _normalize_text(alias)
    exercise = EXERCISE_ALIAS_MAP.get(normalized)
    if exercise:
        return exercise
    suggestions = difflib.get_close_matches(normalized, EXERCISE_ALIAS_MAP.keys(), n=5, cutoff=0.5)
    suggestion_text = ", ".join(suggestions)
    raise ValueError(
        f"Unsupported exercise alias: {alias}. "
        "Use list_strength_exercise_aliases or pass explicit Garmin category/exerciseName values."
        + (f" Close matches: {suggestion_text}." if suggestion_text else "")
    )


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", " ").replace("_", " ").split())


def _get_sport_type(sport_type_key: str) -> dict[str, Any]:
    sport_type = SPORT_TYPE_MAPPING.get(sport_type_key)
    if not sport_type:
        raise ValueError(f"Unsupported sport type: {sport_type_key}")
    return sport_type


def _estimate_duration(steps: list[dict[str, Any]]) -> float:
    total = 0.0
    for step in steps:
        if step["type"] == "RepeatGroupDTO":
            total += step["numberOfIterations"] * _estimate_duration(step["workoutSteps"])
            continue
        if step["endCondition"]["conditionTypeKey"] == "time":
            total += float(step.get("endConditionValue", 0.0))
    return total


def _estimate_distance(steps: list[dict[str, Any]]) -> float:
    total = 0.0
    for step in steps:
        if step["type"] == "RepeatGroupDTO":
            total += step["numberOfIterations"] * _estimate_distance(step["workoutSteps"])
            continue
        if step["endCondition"]["conditionTypeKey"] == "distance":
            total += float(step.get("endConditionValue", 0.0))
    return total
