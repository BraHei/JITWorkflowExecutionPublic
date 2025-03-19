import pytest
import subprocess
from unittest.mock import patch, MagicMock
from flask import Flask
from swagger_server.controllers.health_controller import health_check


@pytest.fixture
def client():
    """Creates a Flask test client for testing the health_check endpoint."""
    app = Flask(__name__)
    app.add_url_rule("/health", view_func=health_check, methods=["GET"])
    with app.test_client() as client:
        yield client


@patch("swagger_server.controllers.health_controller.subprocess.run")
def test_health_check_success(mock_subprocess, client):
    """Tests health_check when Rclone is working (returns 200 OK)."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

    mock_subprocess.assert_called_once_with(["rclone", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@patch("swagger_server.controllers.health_controller.subprocess.run")
def test_health_check_failure(mock_subprocess, client):
    """Tests health_check when Rclone fails (returns 503 Service Unavailable)."""
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_subprocess.return_value = mock_process

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json == {"status": "unhealthy", "error": "Rclone not working"}

    mock_subprocess.assert_called_once_with(["rclone", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@patch("swagger_server.controllers.health_controller.subprocess.run", side_effect=Exception("Unexpected error"))
def test_health_check_exception(mock_subprocess, client):
    """Tests health_check when an exception occurs (returns 503 Service Unavailable)."""
    response = client.get("/health")

    assert response.status_code == 503
    assert response.json == {"status": "unhealthy", "error": "Unexpected error"}

    mock_subprocess.assert_called_once_with(["rclone", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
