import pytest
import json
import base64
import yaml
from unittest.mock import patch, MagicMock
from flask import Flask

mock_secret_data = {
    "username": "test_user",
    "password": "test_password",
    "host": "test_host",
    "database": "test_db",
    "decryption-key": "test_decryption_key"
}

mock_mongo_db_manager = MagicMock()
mock_mongo_db_manager.collection = MagicMock()
mock_mongo_db_manager.collection.find_one.return_value = {"_id": "test_doc_id", "cache": {}}

with patch("swagger_server.managers.awssecretsmanager.get_aws_secret", return_value=mock_secret_data), \
        patch("swagger_server.settings.settings_reader.SettingsReader.load", return_value=None), \
        patch("swagger_server.managers.mongodbmanager.MongoDBManager", return_value=mock_mongo_db_manager):
    from swagger_server.controllers.workflow_controller import workflow_event_handler_post


@pytest.fixture
def client():
    """Creates a Flask test client for the controller tests."""
    app = Flask(__name__)
    app.add_url_rule("/workflow_event", view_func=workflow_event_handler_post, methods=["POST"])
    with app.test_client() as client:
        yield client


@patch("swagger_server.controllers.workflow_controller.workflow_event_handler.handle_workflow_event")
def test_workflow_event_handler_post_valid_json(mock_handler, client):
    """Tests handling a valid JSON workflow event."""
    request_data = {
        "type": "UPDATE",
        "body": {
            "workflow_id": "1234",
            "files": ["file1.txt", "file2.csv"]
        }
    }
    response = client.post("/workflow_event", data=json.dumps(request_data), content_type="application/json")

    assert response.status_code == 200
    assert response.json == {"message": "Workflow UPDATE event handled successfully"}
    mock_handler.assert_called_once_with(request_data["body"])


@patch("swagger_server.controllers.workflow_controller.workflow_event_handler.handle_workflow_event")
def test_workflow_event_handler_post_valid_yaml(mock_handler, client):
    """Tests handling a valid YAML workflow event."""
    request_data_yaml = """
    type: ADD
    body:
      workflow_id: "5678"
      files:
        - file3.txt
        - file4.csv
    """
    response = client.post("/workflow_event", data=request_data_yaml, content_type="application/x-yaml")

    assert response.status_code == 200
    assert response.json == {"message": "Workflow ADD event handled successfully"}
    parsed_yaml = yaml.safe_load(request_data_yaml)
    mock_handler.assert_called_once_with(parsed_yaml["body"])


@patch("swagger_server.controllers.workflow_controller.workflow_event_handler.handle_workflow_event")
def test_workflow_event_handler_post_base64_encoded(mock_handler, client):
    """Tests handling a Base64-encoded workflow event inside workflow_submission."""
    workflow_submission = {
        "workflow_id": "abcd",
        "files": ["file5.txt"]
    }
    encoded_data = base64.b64encode(json.dumps(workflow_submission).encode()).decode()

    request_data = {
        "workflow_submission": {
            "data": encoded_data
        }
    }

    response = client.post("/workflow_event", data=json.dumps(request_data), content_type="application/json")

    assert response.status_code == 200
    assert response.json == {"message": "Base64 decoded workflow event handled successfully"}
    mock_handler.assert_called_once_with(workflow_submission)


def test_workflow_event_handler_post_empty_request(client):
    """Tests handling an empty request body."""
    response = client.post("/workflow_event", data="", content_type="application/json")

    assert response.status_code == 400
    assert response.json == {"error": "Empty request body"}


def test_workflow_event_handler_post_invalid_json(client):
    """Tests handling an invalid JSON request."""
    response = client.post("/workflow_event", data="{invalid_json", content_type="application/json")

    assert response.status_code == 400
    assert response.json == {"error": "Unsupported content type, expecting JSON or YAML"}


def test_workflow_event_handler_post_invalid_yaml(client):
    """Tests handling an invalid YAML request."""
    invalid_yaml = """
    type: ADD
    body:
      workflow_id: "5678
      files:
        - file3.txt
    """
    response = client.post("/workflow_event", data=invalid_yaml, content_type="application/x-yaml")

    assert response.status_code == 400
    assert response.json == {"error": "Unsupported content type, expecting JSON or YAML"}


def test_workflow_event_handler_post_unrecognized_format(client):
    """Tests handling an unrecognized event format."""
    request_data = {
        "unexpected_key": "random_value"
    }
    response = client.post("/workflow_event", data=json.dumps(request_data), content_type="application/json")

    assert response.status_code == 400
    assert response.json == {"error": "Unsupported workflow event format"}


@patch("swagger_server.controllers.workflow_controller.workflow_event_handler.handle_workflow_event")
def test_workflow_event_handler_post_handler_exception(mock_handler, client):
    """Tests error handling when the workflow event handler raises an exception."""
    mock_handler.side_effect = Exception("Unexpected processing error")

    request_data = {
        "type": "UPDATE",
        "body": {
            "workflow_id": "error_case",
            "files": ["error.txt"]
        }
    }

    response = client.post("/workflow_event", data=json.dumps(request_data), content_type="application/json")

    assert response.status_code == 500
    assert response.json == {"error": "Failed to handle UPDATE workflow event: Unexpected processing error"}
    mock_handler.assert_called_once_with(request_data["body"])
