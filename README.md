# Garmin Workouts MCP

`garmin-workouts-mcp` is a standalone MCP server for Garmin Connect workouts.

It is intended as a focused extension for workflows that need a bit more structure around Garmin workout payloads, especially strength training.

This project is packaged as a stdio MCP server and can be published as an OCI image for MCP registries and Glama deployment. It is not a standalone public HTTP MCP endpoint.

<a href="https://glama.ai/mcp/servers/pranciskus/garmin-workouts-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/pranciskus/garmin-workouts-mcp/badge" alt="Garmin Workouts MCP server" />
</a>

## Additions

- Supports Garmin strength workout steps with `reps` end conditions.
- Supports exercise metadata via explicit Garmin enums or friendly aliases.
- Adds `preview_workout_payload` so payloads can be inspected before upload.
- Adds `validate_workout` for early schema and mapping errors.
- Adds `resolve_supported_strength_exercise` for quick mapping checks.
- Adds `get_workout_input_schema` for machine-readable client integration.
- Includes `walking` as a supported sport type, which is also reflected in the prompt/schema.
- Keeps the familiar list/get/delete/schedule/calendar/activity tools.

## Environment

Garmin-backed tools authenticate lazily when they are called:

- Hosted/default path: `GARMIN_EMAIL` and `GARMIN_PASSWORD`
- Local convenience path: `GARTH_HOME` pointing to saved Garmin tokens

The server can start without credentials. Tools that do not talk to Garmin, such as payload preview and schema inspection, still work without secrets.

## Workout Input

The upload and preview tools accept a JSON object shaped like this:

```json
{
  "name": "Upper Day",
  "type": "strength",
  "steps": [
    {
      "stepType": "warmup",
      "endConditionType": "lap.button",
      "stepDescription": "General warm-up"
    },
    {
      "stepType": "interval",
      "exercise": "incline db press",
      "endConditionType": "reps",
      "stepReps": 8,
      "stepDescription": "8-10 reps"
    },
    {
      "stepType": "rest",
      "endConditionType": "time",
      "stepDuration": 120
    }
  ]
}
```

For strength exercises, either pass a friendly alias:

```json
{ "exercise": "t bar row" }
```

or explicit Garmin enums:

```json
{
  "exercise": {
    "category": "ROW",
    "exerciseName": "T_BAR_ROW"
  }
}
```

You can also inspect the accepted structure programmatically through `get_workout_input_schema`, or resolve likely Garmin strength mappings with `resolve_supported_strength_exercise`.

## Development

Run tests in Docker Compose:

```bash
docker compose run --rm tests
```

Build the runtime image:

```bash
docker build -t garmin-workouts-mcp:local .
```

Smoke test the stdio server startup without Garmin credentials:

```bash
python - <<'PY'
import subprocess

proc = subprocess.Popen(
    ["bash", "-lc", "tail -f /dev/null | docker run --rm -i garmin-workouts-mcp:local"]
)
try:
    proc.wait(timeout=5)
    print(f"container exited early with code {proc.returncode}")
finally:
    if proc.poll() is None:
        proc.terminate()
        proc.wait()
        print("container stayed up for 5 seconds")
PY
```

## Publishing

The intended OCI image location is:

```text
ghcr.io/pranciskus/garmin-workouts-mcp
```

Registry metadata lives in [`server.json`](./server.json). The OCI image carries the required label:

```text
io.modelcontextprotocol.server.name=io.github.pranciskus/garmin-workouts-mcp
```

Glama ownership metadata lives in [`glama.json`](./glama.json). It declares the GitHub maintainer account that can claim and manage the Glama listing.

## Glama Submission Checklist

1. Push a semver tag like `v0.1.1`.
2. Confirm the GitHub Actions publish workflow pushed `ghcr.io/pranciskus/garmin-workouts-mcp:<version>` and `:latest`.
3. Confirm the GHCR package is public.
4. Validate [`server.json`](./server.json) and [`glama.json`](./glama.json).
5. Submit the server to the MCP registry using the root `server.json`.
6. On Glama, run the claim ownership flow so it picks up [`glama.json`](./glama.json).
7. After indexing, verify the listing and deployment flow on Glama.