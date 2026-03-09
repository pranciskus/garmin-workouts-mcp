from __future__ import annotations

import pytest

from garmin_workouts_mcp import server


@pytest.fixture(autouse=True)
def reset_auth_state(monkeypatch):
    monkeypatch.setattr(server, "_AUTH_READY", False)


def test_preview_workout_payload_does_not_require_garmin_auth(monkeypatch):
    def fail_auth():
        raise AssertionError("Auth should not be called for preview_workout_payload")

    monkeypatch.setattr(server, "_ensure_authenticated", fail_auth)

    result = server.preview_workout_payload(
        {
            "name": "Preview Only",
            "type": "strength",
            "steps": [
                {
                    "stepType": "interval",
                    "exercise": "leg press",
                    "endConditionType": "reps",
                    "stepReps": 10,
                }
            ],
        }
    )

    assert result["payload"]["workoutName"] == "Preview Only"


def test_garmin_backed_tool_raises_clear_error_without_credentials(monkeypatch):
    monkeypatch.delenv("GARMIN_EMAIL", raising=False)
    monkeypatch.delenv("GARMIN_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="Garmin credentials are required for this tool"):
        server.list_workouts()


def test_env_credentials_are_preferred_for_authentication(monkeypatch):
    calls = []

    monkeypatch.setenv("GARMIN_EMAIL", "user@example.com")
    monkeypatch.setenv("GARMIN_PASSWORD", "secret")
    monkeypatch.setattr(server.garth, "login", lambda email, password: calls.append((email, password)))

    server._ensure_authenticated()

    assert calls == [("user@example.com", "secret")]
