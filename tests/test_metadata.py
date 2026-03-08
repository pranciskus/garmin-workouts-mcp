import json
import tomllib
from pathlib import Path

import httpx
import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SERVER_JSON_PATH = ROOT / "server.json"
GLAMA_JSON_PATH = ROOT / "glama.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"
SCHEMA_URL = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
GLAMA_SCHEMA_URL = "https://glama.ai/mcp/schemas/server.json"
EXPECTED_SERVER_NAME = "io.github.pranciskus/garmin-workouts-mcp"


def load_remote_json(url: str) -> dict:
    response = httpx.get(url, follow_redirects=True, timeout=10)
    response.raise_for_status()
    return response.json()


def test_server_json_matches_pinned_mcp_schema():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    schema = load_remote_json(SCHEMA_URL)
    jsonschema.validate(instance=server_json, schema=schema)


def test_server_json_package_and_project_versions_match():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text())

    project_version = pyproject["project"]["version"]
    assert server_json["version"] == project_version
    assert server_json["packages"][0]["identifier"].endswith(f":{project_version}")


def test_server_json_declares_expected_oci_package():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    package = server_json["packages"][0]

    assert server_json["name"] == EXPECTED_SERVER_NAME
    assert package["registryType"] == "oci"
    assert package["identifier"] == "ghcr.io/pranciskus/garmin-workouts-mcp:0.1.0"
    assert package["runtimeHint"] == "docker"
    assert package["transport"]["type"] == "stdio"

    env_names = {item["name"] for item in package["environmentVariables"]}
    assert env_names == {"GARMIN_EMAIL", "GARMIN_PASSWORD"}


def test_glama_json_matches_schema_and_declares_maintainer():
    glama_json = json.loads(GLAMA_JSON_PATH.read_text())
    schema = load_remote_json(GLAMA_SCHEMA_URL)
    jsonschema.validate(instance=glama_json, schema=schema)

    assert glama_json["maintainers"] == ["pranciskus"]
