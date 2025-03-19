import json
import os
from flask import jsonify, request
from werkzeug.utils import secure_filename

from swagger_server.models.rclone_config_request import RcloneConfigRequest
from swagger_server.models.rclone_copy_request import RcloneCopyRequest
from swagger_server.models.rclone_sync_request import RcloneSyncRequest
from swagger_server.models.rclone_folder_request import RcloneFolderRequest

from ..managers.rclonemanager import RcloneManager

rclone = RcloneManager()


def rclone_check_get(path, file=""):
    """Check if a file or directory exists in Rclone remote storage."""
    success = rclone.check_data_exists(path, file)
    return jsonify({
        "message": f"'{path}':'{file}' exists" if success else f"'{path}':'{file}' does not exist'"
    }), 200 if success else 404


def rclone_copy_post():
    """Copy files using Rclone."""
    body, error = validate_json_request(RcloneCopyRequest)
    if error:
        return error

    if not body.files:
        return jsonify({"error": "No files specified for copying"}), 400

    success, message = rclone.copy_files(body.source, body.destination, body.parallel_files, body.files)
    return jsonify({"message": message} if success else {"error": message}), 200 if success else 500


def rclone_sync_post():
    """Sync folders using Rclone."""
    body, error = validate_json_request(RcloneSyncRequest)
    if error:
        return error

    success, message = rclone.sync_folders(body.source, body.destination, body.parallel_files, body.folders)
    return jsonify({"message": message} if success else {"error": message}), 200 if success else 500


def rclone_get_endpoint_alias_get(endpoint):
    """Get Rclone remote alias from URL."""
    alias = rclone.get_endpoint_name(endpoint)

    if alias:
        return jsonify({"alias": alias}), 200
    return jsonify({"error": f"No alias found for endpoint '{endpoint}'"}), 404


def rclone_configure_post():
    """Adds or updates a Rclone remote."""
    config_request, error = validate_json_request(RcloneConfigRequest)
    if error:
        return error

    success, message = rclone.configure_remote(
        config_request.name, config_request.type, config_request.access_key,
        config_request.secret_key, config_request.endpoint, config_request.remote, config_request.additional_options
    )
    return jsonify({"message": message} if success else {"error": message}), 200 if success else 500


def rclone_configure_get():
    """Retrieves configured Rclone remotes."""
    success, config = rclone.get_remote()

    if success and config:
        try:
            return jsonify(json.loads(config)), 200
        except json.JSONDecodeError:
            return {"error": "Failed to parse Rclone config"}
    return jsonify({"error": config}), 500


def rclone_configure_delete(remote_name):
    """Deletes an Rclone remote."""
    success, message = rclone.delete_remote(remote_name)

    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500


def rclone_create_folder():
    """Create a new folder in a Rclone remote."""
    folder_request, error = validate_json_request(RcloneFolderRequest)
    if error:
        return error

    success, message = rclone.create_folder(folder_request.remote, folder_request.folder)
    return jsonify({"message": message} if success else {"error": message}), 201 if success else 500


def rclone_delete_folder():
    """Delete a folder in an Rclone remote."""

    folder_request, error = validate_json_request(RcloneFolderRequest)
    if error:
        return error

    success, message = rclone.delete_folder(folder_request.remote, folder_request.folder)
    return jsonify({"message": message} if success else {"error": message}), 200 if success else 500

def rclone_list_folders():
    """List all folders in a Rclone remote."""
    remote = request.args.get("remote")

    if not remote:
        return jsonify({"error": "Remote name is required"}), 400

    success, output = rclone.list_folders(remote)

    if success:
        return jsonify({"folders": output}), 200
    return jsonify({"error": f"Failed to list folders: {output}"}), 500

def rclone_list_files(remote, folder):
    """List files in a Rclone remote folder."""
    success, files = rclone.list_files(remote, folder)
    return jsonify(files) if success else jsonify({"error": files}), 200 if success else 500


def rclone_upload_file():
    """Upload a file to a Rclone remote."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    body = request.form
    file = request.files["file"]
    remote, folder = body.get("remote"), body.get("folder", "")

    if not file.filename or not remote:
        return jsonify({"error": "Remote and valid file are required"}), 400

    local_path = f"/tmp/{secure_filename(file.filename)}"
    file.save(local_path)

    # Now, success and message are properly handled
    success, message = rclone.upload_file(remote, folder, local_path)

    os.remove(local_path)

    return jsonify({"message": message} if success else {"error": message}), 201 if success else 500


def rclone_delete_file(remote, file_path):
    """Delete a file from a Rclone remote."""
    success, message = rclone.delete_file(remote, file_path)
    return jsonify({"message": message} if success else {"error": message}), 200 if success else 500


def validate_json_request(model):
    """Validates and parses JSON requests using the given model."""
    if not request.is_json:
        return jsonify({"error": "Invalid JSON format"}), 400

    try:
        return model.from_dict(request.get_json()), None
    except Exception as e:
        return None, jsonify({"error": str(e)}), 400
