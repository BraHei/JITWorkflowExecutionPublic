import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from werkzeug.datastructures import FileStorage
from swagger_server.controllers.rclone_controller import (
    rclone_check_get, rclone_copy_post, rclone_sync_post, rclone_configure_post,
    rclone_configure_get, rclone_configure_delete, rclone_create_folder, rclone_delete_folder,
    rclone_list_folders, rclone_list_files, rclone_upload_file, rclone_delete_file
)


@pytest.fixture
def client():
    """Creates a Flask test client for testing the controller endpoints."""
    app = Flask(__name__)

    # Define routes for the test
    app.add_url_rule("/rclone/check", view_func=rclone_check_get, methods=["GET"])
    app.add_url_rule("/rclone/copy", view_func=rclone_copy_post, methods=["POST"])
    app.add_url_rule("/rclone/sync", view_func=rclone_sync_post, methods=["POST"])
    app.add_url_rule("/rclone/configure", view_func=rclone_configure_post, methods=["POST"])
    app.add_url_rule("/rclone/configure", view_func=rclone_configure_get, methods=["GET"])
    app.add_url_rule("/rclone/configure/<remote_name>", view_func=rclone_configure_delete, methods=["DELETE"])
    app.add_url_rule("/rclone/folder", view_func=rclone_create_folder, methods=["POST"])
    app.add_url_rule("/rclone/folder", view_func=rclone_delete_folder, methods=["DELETE"])
    app.add_url_rule("/rclone/list-folders", view_func=rclone_list_folders, methods=["GET"])
    app.add_url_rule("/rclone/list-files/<remote>/<folder>", view_func=rclone_list_files, methods=["GET"])
    app.add_url_rule("/rclone/upload", view_func=rclone_upload_file, methods=["POST"])
    app.add_url_rule("/rclone/files/<file_path>", view_func=rclone_delete_file, methods=["DELETE"])

    with app.test_client() as client:
        yield client


@patch("swagger_server.controllers.rclone_controller.rclone.copy_files",
       return_value=(True, "Files copied successfully"))
def test_rclone_copy_post_success(mock_copy, client):
    """Test successful Rclone copy operation."""
    response = client.post("/rclone/copy", json={
        "source": "s3://source-bucket",
        "destination": "s3://destination-bucket",
        "parallel_files": 5,
        "files": ["file1.txt", "file2.csv"]
    })
    assert response.status_code == 200
    assert response.json["message"] == "Files copied successfully"
    mock_copy.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.copy_files", return_value=(False, "Copy failed"))
def test_rclone_copy_post_failure(mock_copy, client):
    """Test Rclone copy operation failure."""
    response = client.post("/rclone/copy", json={
        "source": "s3://source-bucket",
        "destination": "s3://destination-bucket",
        "parallel_files": 5,
        "files": ["file1.txt", "file2.csv"]
    })
    assert response.status_code == 500
    assert response.json["error"] == "Copy failed"
    mock_copy.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.sync_folders", return_value=(True, "Sync successful"))
def test_rclone_sync_post_success(mock_sync, client):
    """Test successful Rclone sync operation."""
    response = client.post("/rclone/sync", json={
        "source": "s3://source-bucket",
        "destination": "s3://destination-bucket",
        "parallel_files": 5,
        "folders": ["folder1", "folder2"]
    })
    assert response.status_code == 200
    assert response.json["message"] == "Sync successful"
    mock_sync.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.configure_remote", return_value=(True, "Remote configured"))
def test_rclone_configure_post_success(mock_config, client):
    """Test successful Rclone remote configuration."""
    response = client.post("/rclone/configure", json={
        "name": "myremote",
        "type": "s3",
        "access_key": "ACCESS123",
        "secret_key": "SECRET123",
        "endpoint": "s3.amazonaws.com",
        "remote": "",
        "additional_options": {}
    })
    assert response.status_code == 200
    assert response.json["message"] == "Remote configured"
    mock_config.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.get_remote",
       return_value=(True, '{"remotes": ["myremote"]}'))
def test_rclone_configure_get_success(mock_get_config, client):
    """Test fetching Rclone remote configurations."""
    response = client.get("/rclone/configure")
    assert response.status_code == 200
    assert response.json == {"remotes": ["myremote"]}
    mock_get_config.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.delete_remote", return_value=(True, "Remote deleted"))
def test_rclone_configure_delete_success(mock_delete, client):
    """Test deleting an Rclone remote."""
    response = client.delete("/rclone/configure/myremote")
    assert response.status_code == 200
    assert response.json["message"] == "Remote deleted"
    mock_delete.assert_called_once()


@patch("swagger_server.controllers.rclone_controller.rclone.upload_file", return_value=(True, "File uploaded"))
def test_rclone_upload_file_success(mock_upload, client):
    """Test successful file upload."""
    data = {
        "remote": "s3://bucket",
        "folder": "uploads"
    }
    test_file = FileStorage(stream=open(__file__, "rb"), filename="test.txt", content_type="text/plain")

    response = client.post("/rclone/upload", content_type="multipart/form-data", data={"file": test_file, **data})
    assert response.status_code == 201
    assert response.json["message"] == "File uploaded"
    mock_upload.assert_called_once()
