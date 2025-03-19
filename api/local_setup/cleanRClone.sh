#!/bin/sh
#
# cleanup_rclone_aliases.sh
#
# This script removes the two RClone alias remotes (alias_folder1 and alias_folder2
# by default or custom if arguments are given) and deletes their corresponding folders.

set -euo pipefail

# Check if rclone is installed
if ! command -v rclone &> /dev/null
then
    echo "Error: rclone is not installed or not in PATH."
    echo "Install rclone before running this script."
    exit 1
fi

# If the user provided arguments, use them; otherwise default to "folder1" and "folder2"
FOLDER1="${1:-folder1}"
FOLDER2="${2:-folder2}"

# The aliases to remove
ALIAS1="alias_${FOLDER1}"
ALIAS2="alias_${FOLDER2}"

# Remove the rclone alias remotes
echo "Removing rclone remote '${ALIAS1}'..."
rclone config delete "${ALIAS1}" || echo "Warning: Could not delete remote ${ALIAS1} (it may not exist)."

echo "Removing rclone remote '${ALIAS2}'..."
rclone config delete "${ALIAS2}" || echo "Warning: Could not delete remote ${ALIAS2} (it may not exist)."

# Remove the folders from the current directory
echo "Removing folders '${FOLDER1}' and '${FOLDER2}' in the current directory..."
rm -rf "${FOLDER1}" "${FOLDER2}"

echo "Cleanup complete! Removed aliases '${ALIAS1}', '${ALIAS2}' and folders '${FOLDER1}', '${FOLDER2}'."

