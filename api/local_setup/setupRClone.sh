#!/bin/sh
#
# setup_rclone_aliases.sh
#
# This script sets up two RClone alias remotes for folders within
# the current working directory.

# Exit on errors or uninitialized variables:
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

# The current directory path
CURRENT_DIR="$(pwd)"

# Optional: Confirm that the specified folders exist.
# If you'd like the script to auto-create them, uncomment the mkdir lines.
for FOLDER in "$FOLDER1" "$FOLDER2"; do
    if [ ! -d "$FOLDER" ]; then
        echo "Warning: '$FOLDER' does not exist in $CURRENT_DIR."
        # Uncomment the line below if you want to create folders automatically:
        mkdir -p "$FOLDER"
        echo "Created folder: $CURRENT_DIR/$FOLDER"
    fi
done

# Add three test files to folder2
cp $CURRENT_DIR/file1.txt $FOLDER2/file1.txt
cp $CURRENT_DIR/file2.txt $FOLDER2/file2.txt
cp $CURRENT_DIR/file3.txt $FOLDER2/file3.txt
echo "Created 3 files in $FOLDER2"

# Create the first alias remote
echo "Creating alias remote 'alias_${FOLDER1}' for '${CURRENT_DIR}/${FOLDER1}'..."
rclone config create "alias_${FOLDER1}" alias remote "${CURRENT_DIR}/${FOLDER1}"

# Create the second alias remote
echo "Creating alias remote 'alias_${FOLDER2}' for '${CURRENT_DIR}/${FOLDER2}'..."
rclone config create "alias_${FOLDER2}" alias remote "${CURRENT_DIR}/${FOLDER2}"

echo "Done!"
echo "You can now use them in RClone commands as 'alias_${FOLDER1}:' and 'alias_${FOLDER2}:'"

