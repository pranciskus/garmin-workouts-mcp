import json
import tomllib
import urllib.request
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SERVER_JSON_PATH = ROOT / "server.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"
SCHEMA_URL = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
EXPECTED_SERVER_NAME = "io.github.pranciskus/garmin-workouts-mcp"


def test_server_json_matches_pinned_mcp_schema():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    with urllib.request.urlopen(SCHEMA_URL, timeout=10) as response:
        schema = json.load(response)
    jsonschema.validate(instance=server_json, schema=schema)


def test_server_json_package_and_project_versions_match():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text())

    project_version = pyproject["project"]["version"]
    assert server_json["version"] == project_version
    assert server_json["packages"][0]["version"] == project_version


def test_server_json_declares_expected_oci_package():
    server_json = json.loads(SERVER_JSON_PATH.read_text())
    package = server_json["packages"][0]

    assert server_json["name"] == EXPECTED_SERVER_NAME
    assert package["registryType"] == "oci"
    assert package["identifier"] == "ghcr.io/pranciskus/garmin-workouts-mcp"
    assert package["runtimeHint"] == "docker"
    assert package["transport"]["type"] == "stdio"

    env_names = {item["name"] for item in package["environmentVariables"]}
    assert env_names == {"GARMIN_EMAIL", "GARMIN_PASSWORD"}

