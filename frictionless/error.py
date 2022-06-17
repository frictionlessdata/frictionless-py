from __future__ import annotations
from typing import List
from importlib import import_module
from .metadata import Metadata
from . import helpers


# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.
# Also, validation is disabled for performance reasons at the moment.
# Allow creating from a descriptor (note needs to be optional)


class Error(Metadata):
    """Error representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import errors`

    Parameters:
        descriptor? (str|dict): error descriptor
        note (str): an error note

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    code: str = "error"
    name: str = "Error"
    tags: List[str] = []
    template: str = "{note}"
    description: str = "Error"

    def __init__(self, descriptor=None, *, note: str):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.setinitial("name", self.name)
        self.setinitial("tags", self.tags)
        self.setinitial("note", note)
        self.setinitial("message", helpers.safe_format(self.template, self))
        self.setinitial("description", self.description)

    @property
    def note(self) -> str:
        """
        Returns:
            str: note
        """
        return self["note"]

    @property
    def message(self) -> str:
        """
        Returns:
            str: message
        """
        return self["message"]

    # Convert

    # TODO: review
    @classmethod
    def from_descriptor(cls, descriptor):
        system = import_module("frictionless").system
        return system.create_error(descriptor)
