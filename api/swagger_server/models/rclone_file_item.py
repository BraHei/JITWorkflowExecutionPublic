# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import Dict, Any  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util

class RcloneFileItem(Model):
    """
    Data model representing a file in an Rclone remote.
    """

    def __init__(self, file_name: str, size: int):
        """
        Initialize RcloneFileItem.

        :param file_name: Name of the file.
        :param size: Size of the file in bytes.
        """
        self.file_name = file_name
        self.size = size

    @classmethod
    def from_dict(cls, data: dict):
        """
        Convert dictionary to RcloneFileItem object.
        """
        return cls(
            file_name=data.get("file_name"),
            size=data.get("size"),
        )
