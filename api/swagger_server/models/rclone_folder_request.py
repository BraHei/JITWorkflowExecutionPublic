# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import Dict, Any  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util

class RcloneFolderRequest(Model):
    """
    Data model for creating or deleting a folder in an Rclone remote.
    """

    def __init__(self, remote: str, folder: str):
        """
        Initialize RcloneFolderRequest.

        :param remote: Name of the Rclone remote (e.g., "primary-storage").
        :param folder: Name of the folder to create or delete.
        """
        self.remote = remote
        self.folder = folder

    @classmethod
    def from_dict(cls, data: dict):
        """
        Convert dictionary to RcloneFolderRequest object.
        """
        return cls(
            remote=data.get("remote"),
            folder=data.get("folder"),
        )
