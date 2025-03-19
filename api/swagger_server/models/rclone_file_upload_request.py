# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import Dict, Any  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util

class RcloneFileUploadRequest(Model):
    """
    Data model for uploading a file to an Rclone remote.
    """

    def __init__(self, remote: str, folder: str, file: Any):
        """
        Initialize RcloneFileUploadRequest.

        :param remote: Name of the Rclone remote (e.g., "primary-storage").
        :param folder: Destination folder in the remote.
        :param file: The file object to be uploaded.
        """
        self.remote = remote
        self.folder = folder
        self.file = file

    @classmethod
    def from_dict(cls, data: dict):
        """
        Convert dictionary to RcloneFileUploadRequest object.
        """
        return cls(
            remote=data.get("remote"),
            folder=data.get("folder"),
            file=data.get("file"),
        )
