from flask import jsonify
import subprocess

def health_check():  # noqa: E501
    """
    Health check endpoint for the replication service.

    Returns:
        200 - If the service is healthy
        503 - If the service is unhealthy
    """
    try:
        # Perform a basic system health check (modify this if needed)
        rclone_status = subprocess.run(["rclone", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rclone_healthy = rclone_status.returncode == 0

        if rclone_healthy:
            return jsonify({"status": "healthy"}), 200
        else:
            return jsonify({"status": "unhealthy", "error": "Rclone not working"}), 503

    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503
