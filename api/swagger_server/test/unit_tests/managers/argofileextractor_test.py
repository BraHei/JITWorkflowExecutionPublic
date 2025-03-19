import pytest
import json
import yaml
from swagger_server.managers.argofileextractor import clean_yaml_input, parse_argo_workflow


def test_clean_yaml_input_valid_yaml():
    """Tests that clean_yaml_input returns valid YAML content when given proper input."""
    raw_yaml = """metadata:
  name: test-workflow
  uid: 12345
"""
    assert clean_yaml_input(raw_yaml) == raw_yaml


def test_clean_yaml_input_with_preamble():
    """Tests that clean_yaml_input correctly removes log preambles."""
    raw_yaml = """2023-03-10T12:00:00 INFO: Workflow started
{ "metadata": { "name": "test-workflow", "uid": "12345" } }
"""
    expected_output = '{ "metadata": { "name": "test-workflow", "uid": "12345" } }\n'
    assert clean_yaml_input(raw_yaml) == expected_output


def test_clean_yaml_input_invalid_format():
    """Tests that clean_yaml_input does not modify malformed input."""
    raw_yaml = "!!!INVALID DATA!!!"
    assert clean_yaml_input(raw_yaml) == raw_yaml


def test_parse_argo_workflow_valid_yaml():
    """Tests parsing a valid Argo workflow YAML input."""
    yaml_input = """
metadata:
  name: test-workflow
  uid: test-uid
  labels:
    workflows.argoproj.io/phase: Running
spec:
  arguments:
    parameters:
      - name: files
        value: '["file1.txt", "file2.csv"]'
      - name: primary_endpoint
        value: "s3://primary-bucket/"
      - name: secondary_endpoint
        value: "s3://secondary-bucket/"
      - name: primary_folder
        value: "primary-folder/"
      - name: secondary_folder
        value: "secondary-folder/"
status:
  phase: Running
"""
    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": "s3://primary-bucket/",
        "secondary_endpoint": "s3://secondary-bucket/",
        "primary_folder": "primary-folder/",
        "secondary_folder": "secondary-folder/",
        "endpoint_type": "DUAL",
        "files": ["file1.txt", "file2.csv"],
        "status": "RUNNING",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_invalid_yaml():
    """Tests parsing an invalid YAML string."""
    invalid_yaml = """invalid_key: : : :"""
    result = parse_argo_workflow(invalid_yaml)
    assert "error" in result


def test_parse_argo_workflow_missing_parameters():
    """Tests handling of missing parameters in the workflow."""
    yaml_input = """
metadata:
  name: test-workflow
  uid: test-uid
spec:
  arguments:
    parameters: []
status:
  phase: Succeeded
"""
    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": None,
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "UNKNOWN",
        "files": [],
        "status": "SUCCEEDED",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_with_only_primary():
    """Tests a workflow with only a primary endpoint."""
    yaml_input = """
metadata:
  uid: "test-uid"
spec:
  arguments:
    parameters:
      - name: primary_endpoint
        value: "s3://primary-bucket/"
status:
  phase: Running
"""
    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": "s3://primary-bucket/",
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "PRIMARY_ONLY",
        "files": [],
        "status": "RUNNING",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_with_only_secondary():
    """Tests a workflow with only a secondary endpoint."""
    yaml_input = """
metadata:
  uid: "test-uid"
spec:
  arguments:
    parameters:
      - name: secondary_endpoint
        value: "s3://secondary-bucket/"
status:
  phase: Failed
"""
    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": None,
        "secondary_endpoint": "s3://secondary-bucket/",
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "SECONDARY_ONLY",
        "files": [],
        "status": "FAILED",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_no_metadata():
    """Tests handling of workflows without metadata."""
    yaml_input = """
spec:
  arguments:
    parameters:
      - name: files
        value: '["file1.txt"]'
status:
  phase: Succeeded
"""
    expected_output = {
        "unique_id": None,
        "event_type": "UNKNOWN",
        "primary_endpoint": None,
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "UNKNOWN",
        "files": ["file1.txt"],
        "status": "SUCCEEDED",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_no_status():
    """Tests handling of workflows without a status field."""
    yaml_input = """
metadata:
  uid: "test-uid"
spec:
  arguments:
    parameters:
      - name: files
        value: '["file1.txt"]'
"""
    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": None,
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "UNKNOWN",
        "files": ["file1.txt"],
        "status": "UNKNOWN",
    }

    assert parse_argo_workflow(yaml_input) == expected_output


def test_parse_argo_workflow_handles_json_input():
    """Tests parsing a JSON input instead of YAML."""
    json_input = json.dumps({
        "metadata": {"uid": "test-uid"},
        "spec": {
            "arguments": {
                "parameters": [
                    {"name": "files", "value": '["file1.txt"]'}
                ]
            }
        },
        "status": {"phase": "Succeeded"}
    })

    expected_output = {
        "unique_id": "test-uid",
        "event_type": "UNKNOWN",
        "primary_endpoint": None,
        "secondary_endpoint": None,
        "primary_folder": None,
        "secondary_folder": None,
        "endpoint_type": "UNKNOWN",
        "files": ["file1.txt"],
        "status": "SUCCEEDED",
    }

    assert parse_argo_workflow(json_input) == expected_output
