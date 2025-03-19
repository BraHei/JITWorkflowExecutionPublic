import json
import subprocess
import colorama
from pathlib import Path

colorama.init(autoreset=True)


def handle_rclone_command(command):
    """
    Executes a Rclone command using subprocess.

    Args:
        command (list): The Rclone command as a list of arguments.

    Returns:
        tuple(bool, str): (Success, Command output or error message)
    """
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        error_message = result.stderr.strip()
        return False, error_message


class RcloneManager:
    def __init__(self):
        """
        Initializes the RcloneManager by loading configured endpoints.
        Calls `update_endpoints()` to retrieve current Rclone configurations.
        """
        self.endpoints = {}
        self.update_endpoints()

    def update_endpoints(self):
        """
        Retrieves and updates the configured endpoints using `rclone config dump`.
        Parses the JSON output and stores the endpoint configurations.
        """
        success, output = handle_rclone_command(["rclone", "config", "dump"])
        if success and output:
            try:
                self.endpoints = json.loads(output)
            except json.JSONDecodeError:
                self.endpoints = {}
        else:
            self.endpoints = {}

    def configure_remote(self, name, remote_type, access_key, secret_key, endpoint, remote="", additional_options=None):
        """
        Configures a Rclone remote dynamically.
        """
        cmd = [
            "rclone", "config", "create", name, remote_type,
            "access_key_id", access_key,
            "secret_access_key", secret_key,
            "endpoint", endpoint
        ]

        if remote:
            cmd.extend(["remote", remote])

        if additional_options and isinstance(additional_options, dict):
            for key, value in additional_options.items():
                if isinstance(value, str):
                    cmd.extend([key, value])
                elif isinstance(value, (list, tuple)):
                    cmd.extend([key, " ".join(map(str, value))])
                else:
                    cmd.extend([key, str(value)])

        return handle_rclone_command(cmd)

    def get_remote(self):
        """
        Retrieves configured Rclone remotes.
        """
        return handle_rclone_command(["rclone", "config", "dump"])

    def delete_remote(self, remote_name):
        """
        Deletes a Rclone remote configuration.
        """
        success, output = handle_rclone_command(["rclone", "config", "delete", remote_name])
        if success:
            return True, f"Remote '{remote_name}' deleted successfully"
        return False, output

    def create_folder(self, remote, folder):
        """
        Creates a new folder in a Rclone remote.
        """
        success, output = handle_rclone_command(["rclone", "mkdir", f"{remote}{folder}", "--s3-no-check-bucket"])

        if success:
            return True, f"Folder '{folder}' created in '{remote}'"
        return False, f"Failed to create folder '{folder}' in '{remote}': {output}"

    def delete_folder(self, remote, folder):
        """
        Deletes a folder in a Rclone remote.
        """
        success, output = handle_rclone_command(["rclone", "purge", f"{remote}{folder}", "--s3-no-check-bucket"])

        if success:
            return True, f"Folder '{folder}' deleted in '{remote}'"
        return False, f"Failed to delete folder '{folder}' in '{remote}': {output}"

    def list_files(self, remote, folder=""):
        """
        Lists files in a Rclone remote folder.
        """
        success, output = handle_rclone_command(["rclone", "ls", f"{remote}{folder}", "--s3-no-check-bucket"])
        if success and output:
            files = []
            for line in output.split("\n"):
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    files.append({"file_name": parts[1], "size": int(parts[0])})
            return True, files
        return False, output

    def list_folders(self, remote):
        """
        Lists all folders in a Rclone remote.

        Args:
            remote (str): The Rclone remote name.

        Returns:
            tuple: (success: bool, folders: list or error message)
        """
        success, output = handle_rclone_command(["rclone", "lsd", f"{remote}:"], "--s3-no-check-bucket")

        if success:
            folders = [line.split()[-1] for line in output.split("\n") if line.strip()]
            return True, folders
        return False, output

    def upload_file(self, remote, folder, file_path):
        """
        Uploads a file to a Rclone remote.

        Returns:
            tuple(bool, str): (Success, Command output or error message)
        """
        file_name = Path(file_path).name
        remote_path = f"{remote}{folder}/{file_name}"

        success, message = handle_rclone_command(["rclone", "copyto", file_path, remote_path, "--s3-no-check-bucket"])

        if success:
            return True, f"File '{file_name}' uploaded to '{remote}/{folder}'"
        return False, f"Failed to upload '{file_name}' to '{remote}/{folder}': {message}"

    def delete_file(self, remote, file_path):
        """
        Deletes a file from a Rclone remote.
        """
        success, _ = handle_rclone_command(["rclone", "delete", f"{remote}{file_path}", "--s3-no-check-bucket"])
        return success

    def check_data_exists(self, remote, path=""):
        """
        Checks if a given file or directory exists in Rclone storage.
        """

        """
        Verifies if a given file or directory exists in remote storage.

        Args:
            data_path (str): The path to check.

        Returns:
            bool: True if the data exists, False otherwise.
        """

        full_path = f"{remote}"
        if path:
            full_path = f"{remote}{path}"

        success, existing_file = handle_rclone_command(["rclone", "ls", full_path, "--s3-no-check-bucket"])

        if not success or not existing_file:
            return False
        return True

    def get_endpoint_name(self, endpoint_url):
        """
        Returns the alias matching the given endpoint URL.
        If the passed string is itself an alias, it also returns that alias.
        If none is found, returns None.
        """
        self.update_endpoints()
        for alias, config in self.endpoints.items():
            # If endpoint_url matches the alias or the endpoint value, return alias
            if alias == endpoint_url or config.get("endpoint") == endpoint_url:
                return alias
        return None

    def sync_folders(self, source, destination, parallel_files=1, folders=None):
        """
        Synchronizes folders between a source and a destination using `rclone sync`.
        """
        """
            Synchronizes folders between a source and a destination using `rclone sync`.

            Args:
                source (str): The source remote.
                destination (str): The destination remote.
                parallel_files (int): Number of parallel file transfers.
                folders (list, optional): List of folders to sync.

            Returns:
                tuple(bool, str): (Success, message)
            """
        if folders:
            for folder in folders:
                folder_source = f"{source}{folder}"
                folder_destination = f"{destination}{folder}"
                success, output = handle_rclone_command([
                    "rclone", "sync", folder_source, folder_destination,
                    "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
                ])
                if not success:
                    return False, f"Failed to sync {folder}: {output}"
            return True, "All folders synchronized successfully."

        success, output = handle_rclone_command([
            "rclone", "sync", source, destination,
            "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
        ])

        return (success, "Folders synchronized successfully.") if success else (False, f"Sync failed: {output}")

    def copy_folders(self, source, destination, parallel_files=1, folders=None):
        """
        Copies folders from a source to a destination using `rclone copy`.
        """
        if folders:
            for folder in folders:
                folder_source = f"{source}{folder}"
                folder_destination = f"{destination}{folder}"
                handle_rclone_command([
                    "rclone", "copy", folder_source, folder_destination,
                    "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
                ])
        else:
            handle_rclone_command([
                "rclone", "copy", source, destination,
                "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
            ])

    def copy_files(self, source, destination, parallel_files=1, files=None):
        """
        Copies files between a source and a destination using `rclone copy`.

        Args:
            source (str): The source remote.
            destination (str): The destination remote.
            parallel_files (int): Number of parallel file transfers.
            files (list, optional): List of files to copy.

        Returns:
            tuple(bool, str): (Success, message)
        """
        if files:
            for file in files:
                file_source = f"{source}{file}"
                file_destination = f"{destination}{file}"
                success, output = handle_rclone_command([
                    "rclone", "copyto", file_source, file_destination,
                    "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
                ])
                if not success:
                    return False, f"Failed to copy {file}: {output}"
            return True, "All files copied successfully."

        success, output = handle_rclone_command([
            "rclone", "copy", source, destination,
            "--progress", f"--transfers={parallel_files}", "--s3-no-check-bucket"
        ])

        return (success, "Files copied successfully.") if success else (False, f"Copy failed: {output}")

    def get_remote_used_storage(self, endpoint, folder):
        """
        Retrieves the used storage capacity of a given Rclone remote.

        Args:
            endpoint (str): The Rclone remote name (e.g., "UvA").
            folder (str): The folder path in the remote (e.g., "naa-vre-user-data/lifewatchminio@hayblock.nl").

        Returns:
            tuple: (bool, int or str) - Success flag and used storage in bytes or error message.
        """
        # Construct the correct rclone command
        rclone_command = ["rclone", "size", f"{endpoint}{folder}", "--json"]

        try:
            # Run the command and capture the output
            result = subprocess.run(rclone_command, capture_output=True, text=True, check=True)
            output = result.stdout

            # Parse JSON output
            storage_info = json.loads(output)
            if "bytes" in storage_info:
                return True, int(storage_info["bytes"])
            return False, "Available storage information not found."

        except subprocess.CalledProcessError as e:
            return False, f"Rclone command failed: {e.stderr}"
        except json.JSONDecodeError:
            return False, "Failed to parse JSON output."

    def get_remote_file_size(self, remote: str, filename: str):
        """
        Retrieves the size of a specific file in the given Rclone remote.

        Args:
            remote (str): The Rclone remote name (e.g., "remote_minio:").
            filename (str): The file path relative to the remote.

        Returns:
            tuple: (bool, int or str) - Success flag and file size in bytes or error message.
        """
        success, output = handle_rclone_command(["rclone", "lsl", f"{remote}{filename}"])

        if success:
            parts = output.split(maxsplit=3)  # Split into at most 3 parts: size, timestamp, filename
            if len(parts) < 3:
                return False, "Unexpected output format from rclone lsl"

            file_size = int(parts[0])  # First part is file size in bytes
            return True, file_size

        return False, output  # Return error message if command failed

    def get_files_to_transfer(self, endpoint: str, requested_files: list) -> list:
        """
        Determines which files are missing from the primary storage and need to be copied from secondary storage.

        Args:
            requested_files (list): List of filenames to check.

        Returns:
            list: List of filenames that need to be transferred from secondary to primary.
        """
        files_to_transfer = [filename for filename in requested_files if
                             not self.check_data_exists(f"{endpoint}{filename}")]

        return files_to_transfer


# Example usage
if __name__ == "__main__":
    rclone = RcloneManager()
    rclone.sync_folders("source_remote", "destination_remote", parallel_files=2, folders=["folder1", "folder2"])
