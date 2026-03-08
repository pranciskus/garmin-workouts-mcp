import pytest

from garmin_workouts_mcp.payloads import (
    build_workout_payload,
    describe_workout,
    resolve_strength_exercise,
)


def test_strength_workout_builds_with_mapped_exercise_names():
    payload = build_workout_payload(
        {
            "name": "Upper",
            "type": "strength",
            "steps": [
                {
                    "stepType": "warmup",
                    "endConditionType": "lap.button",
                    "stepDescription": "General warm-up",
                },
                {
                    "stepType": "interval",
                    "exercise": "incline db press",
                    "endConditionType": "reps",
                    "stepReps": 8,
                    "stepDescription": "8-10 reps",
                },
                {
                    "stepType": "rest",
                    "endConditionType": "time",
                    "stepDuration": 120,
                },
            ],
        }
    )

    steps = payload["workoutSegments"][0]["workoutSteps"]
    assert steps[1]["endCondition"]["conditionTypeKey"] == "reps"
    assert steps[1]["category"] == "BENCH_PRESS"
    assert steps[1]["exerciseName"] == "INCLINE_DUMBBELL_BENCH_PRESS"
    assert payload["estimatedDurationInSecs"] == 120.0


def test_strength_rep_steps_require_exercise_mapping():
    with pytest.raises(ValueError, match="missing exercise mapping"):
        build_workout_payload(
            {
                "name": "Broken Strength",
                "type": "strength",
                "steps": [
                    {
                        "stepType": "interval",
                        "endConditionType": "reps",
                        "stepReps": 10,
                    }
                ],
            }
        )


def test_running_distance_and_time_steps_still_work():
    payload = build_workout_payload(
        {
            "name": "Intervals",
            "type": "running",
            "steps": [
                {
                    "stepType": "warmup",
                    "endConditionType": "time",
                    "stepDuration": 600,
                },
                {
                    "stepType": "interval",
                    "endConditionType": "distance",
                    "stepDistance": 1,
                    "distanceUnit": "km",
                    "target": {"type": "pace", "value": [4.5, 5.0], "unit": "min_per_km"},
                },
            ],
        }
    )

    steps = payload["workoutSegments"][0]["workoutSteps"]
    assert steps[0]["endConditionValue"] == 600.0
    assert steps[1]["endConditionValue"] == 1000.0
    assert steps[1]["targetType"]["workoutTargetTypeKey"] == "pace.zone"
    assert payload["estimatedDistanceInMeters"] == 1000.0


def test_describe_workout_reports_strength_step_summary():
    summary = describe_workout(
        {
            "name": "Lower",
            "type": "strength",
            "steps": [
                {
                    "stepType": "interval",
                    "exercise": {
                        "category": "SQUAT",
                        "exerciseName": "LEG_PRESS",
                    },
                    "endConditionType": "reps",
                    "stepReps": 12,
                }
            ],
        }
    )

    assert summary["repStepCount"] == 1
    assert summary["mappedStrengthExerciseCount"] == 1


def test_resolve_strength_exercise_returns_close_matches():
    result = resolve_strength_exercise("incline db prs")

    assert result["matched"] is False
    assert result["suggestions"]
    assert result["suggestions"][0]["alias"] == "incline db press"
