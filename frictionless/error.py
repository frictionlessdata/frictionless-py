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

    name: str = field(init=False, default="Error")
    type: str = field(init=False, default="error")
    tags: List[str] = field(init=False, default_factory=list)
    template: str = field(init=False, default="{note}")
    description: str = field(init=False, default="Error")

    def __post_init__(self):
        descriptor = self.metadata_export(exclude=["message"])
        self.message = helpers.safe_format(self.template, descriptor)
        # TODO: review this situation -- why we set it by hands??
        self.metadata_assigned.add("name")
        self.metadata_assigned.add("tags")
        self.metadata_assigned.add("message")
        self.metadata_assigned.add("description")

    # State

    note: str
    """TODO: add docs"""

    message: str = field(init=False)
    """TODO: add docs"""

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["note"],
        "properties": {
            "name": {},
            "type": {},
            "tags": {},
            "description": {},
            "message": {},
            "note": {},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        system = import_module("frictionless").system
        return system.create_error(descriptor)
