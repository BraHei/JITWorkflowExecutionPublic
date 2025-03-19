import pytest
import subprocess
import os
import time
from swagger_server.managers.rclonemanager import RcloneManager


@pytest.fixture(scope="module")
def rclone():
    """Fixture that initializes and returns an instance of RcloneManager."""
    return RcloneManager()


@pytest.fixture(scope="module")
def setup_rclone_remote(rclone):
    """Creates a temporary Rclone remote for testing."""
    remote_name = "test_remote"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    endpoint = "http://localhost:9000"

    success, message = rclone.configure_remote(remote_name, "s3", access_key, secret_key, endpoint)

    if not success:
        pytest.fail(f"Failed to configure remote: {message}")

    yield remote_name

    rclone.delete_remote(remote_name)


def test_rclone_configure_remote(rclone, setup_rclone_remote):
    """Tests setting up an Rclone remote."""
    remote_name = setup_rclone_remote
    success, output = rclone.get_remote()

    assert success
    assert remote_name in output, f"Remote {remote_name} not found in configuration"


def test_rclone_create_folder(rclone, setup_rclone_remote):
    """Tests creating a folder inside the Rclone remote."""
    remote_name = setup_rclone_remote
    folder_name = "/test_folder"

    success, message = rclone.create_folder(remote_name, folder_name)

    assert success
    assert message == f"Folder '/test_folder' created in 'test_remote'"


def test_rclone_upload_file(rclone, setup_rclone_remote):
    """Tests uploading a file to the Rclone remote."""
    remote_name = setup_rclone_remote
    folder_name = "/test_folder"
    file_name = "test_file.txt"

    local_file_path = f"/tmp/{file_name}"
    with open(local_file_path, "w") as f:
        f.write("Test file content")

    success, message = rclone.upload_file(remote_name, folder_name, local_file_path)

    assert success, f"Failed to upload file: {message}"

    success, files = rclone.list_files(remote_name, folder_name)
    assert success
    assert any(f["file_name"] == file_name for f in files)

    os.remove(local_file_path)


def test_rclone_list_files(rclone, setup_rclone_remote):
    """Tests listing files inside the Rclone remote."""
    remote_name = setup_rclone_remote
    folder_name = "/test_folder"

    success, files = rclone.list_files(remote_name, folder_name)

    assert success
    assert len(files) > 0


def test_rclone_delete_file(rclone, setup_rclone_remote):
    """Tests deleting a file from the Rclone remote."""
    remote_name = setup_rclone_remote
    folder_name = "/test_folder"
    file_name = "test_file.txt"

    success = rclone.delete_file(remote_name, f"{folder_name}/{file_name}")

    assert success


def test_rclone_delete_folder(rclone, setup_rclone_remote):
    """Tests deleting a folder from the Rclone remote."""
    remote_name = setup_rclone_remote
    folder_name = "/test_folder"

    success, message = rclone.delete_folder(remote_name, folder_name)

    assert success, "Failed to delete folder"
    assert message == f"Folder '/test_folder' deleted in 'test_remote'"
