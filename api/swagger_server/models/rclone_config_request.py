# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict, Any  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util

class RcloneConfigRequest(Model):
    """
    Data model for Rclone remote configuration.
    """

    def __init__(self, name: str, stype: str, access_key: str, secret_key: str, endpoint: str, remote: str = "", additional_options: Dict[str, Any] = None):
        self.name = name
        self.type = stype
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.remote = remote
        self.additional_options = additional_options or {}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name"),
            stype=data.get("type"),
            access_key=data.get("access_key"),
            secret_key=data.get("secret_key"),
            endpoint=data.get("endpoint"),
            remote=data.get("remote"),
            additional_options=data.get("additional_options", {}),
        )
