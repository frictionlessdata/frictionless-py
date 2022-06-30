from __future__ import annotations
from typing import List
from importlib import import_module
from dataclasses import dataclass, field
from .metadata import Metadata
from . import helpers


# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.


@dataclass
class Error(Metadata):
    """Error representation"""

    # State

    code: str = field(init=False, default="error")
    """TODO: add docs"""

    name: str = field(init=False, default="Error")
    """TODO: add docs"""

    tags: List[str] = field(init=False, default_factory=list)
    """TODO: add docs"""

    template: str = field(init=False, default="{note}")
    """TODO: add docs"""

    description: str = field(init=False, default="Error")
    """TODO: add docs"""

    note: str
    """TODO: add docs"""

    # Props

    @property
    def message(self) -> str:
        """Error message"""
        return helpers.safe_format(self.template, self)

    # Convert

    # TODO: review
    @classmethod
    def from_descriptor(cls, descriptor):
        system = import_module("frictionless").system
        return system.create_error(descriptor)

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "code": {},
            "note": {},
            "name": {},
            "tags": {},
            "message": {},
            "description": {},
        },
    }
