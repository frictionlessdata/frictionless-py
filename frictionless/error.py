from __future__ import annotations
import attrs
from typing import List, ClassVar
from importlib import import_module
from .metadata import Metadata
from . import helpers


# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.


@attrs.define(kw_only=True)
class Error(Metadata):
    """Error representation"""

    type: ClassVar[str] = "error"
    title: ClassVar[str] = "Error"
    description: ClassVar[str] = "Error"
    template: ClassVar[str] = "{note}"
    tags: ClassVar[List[str]] = []

    def __attrs_post_init__(self):
        descriptor = self.metadata_export(exclude=["message"])
        self.message = helpers.safe_format(self.template, descriptor)
        # TODO: review this situation -- why we set it by hands??
        self.metadata_assigned.add("title")
        self.metadata_assigned.add("description")
        self.metadata_assigned.add("message")
        self.metadata_assigned.add("tags")

    # State

    message: str = attrs.field(init=False)
    """TODO: add docs"""

    note: str
    """TODO: add docs"""

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": ["type", "title", "description", "message", "tags", "note"],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "message": {"type": "string"},
            "tags": {"type": "array"},
            "note": {"type": "string"},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        system = import_module("frictionless").system
        return system.create_error(descriptor)
