# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class RcloneSyncRequest(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, source: str=None, destination: str=None, parallel_files: int=1, folders: List[str]=None):  # noqa: E501
        """RcloneSyncRequest - a model defined in Swagger

        :param source: The source of this RcloneSyncRequest.  # noqa: E501
        :type source: str
        :param destination: The destination of this RcloneSyncRequest.  # noqa: E501
        :type destination: str
        :param parallel_files: The parallel_files of this RcloneSyncRequest.  # noqa: E501
        :type parallel_files: int
        :param folders: The folders of this RcloneSyncRequest.  # noqa: E501
        :type folders: List[str]
        """
        self.swagger_types = {
            'source': str,
            'destination': str,
            'parallel_files': int,
            'folders': List[str]
        }

        self.attribute_map = {
            'source': 'source',
            'destination': 'destination',
            'parallel_files': 'parallel_files',
            'folders': 'folders'
        }
        self._source = source
        self._destination = destination
        self._parallel_files = parallel_files
        self._folders = folders

    @classmethod
    def from_dict(cls, dikt) -> 'RcloneSyncRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The RcloneSyncRequest of this RcloneSyncRequest.  # noqa: E501
        :rtype: RcloneSyncRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def source(self) -> str:
        """Gets the source of this RcloneSyncRequest.


        :return: The source of this RcloneSyncRequest.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source: str):
        """Sets the source of this RcloneSyncRequest.


        :param source: The source of this RcloneSyncRequest.
        :type source: str
        """

        self._source = source

    @property
    def destination(self) -> str:
        """Gets the destination of this RcloneSyncRequest.


        :return: The destination of this RcloneSyncRequest.
        :rtype: str
        """
        return self._destination

    @destination.setter
    def destination(self, destination: str):
        """Sets the destination of this RcloneSyncRequest.


        :param destination: The destination of this RcloneSyncRequest.
        :type destination: str
        """

        self._destination = destination

    @property
    def parallel_files(self) -> int:
        """Gets the parallel_files of this RcloneSyncRequest.


        :return: The parallel_files of this RcloneSyncRequest.
        :rtype: int
        """
        return self._parallel_files

    @parallel_files.setter
    def parallel_files(self, parallel_files: int):
        """Sets the parallel_files of this RcloneSyncRequest.


        :param parallel_files: The parallel_files of this RcloneSyncRequest.
        :type parallel_files: int
        """

        self._parallel_files = parallel_files

    @property
    def folders(self) -> List[str]:
        """Gets the folders of this RcloneSyncRequest.


        :return: The folders of this RcloneSyncRequest.
        :rtype: List[str]
        """
        return self._folders

    @folders.setter
    def folders(self, folders: List[str]):
        """Sets the folders of this RcloneSyncRequest.


        :param folders: The folders of this RcloneSyncRequest.
        :type folders: List[str]
        """

        self._folders = folders
