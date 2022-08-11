from __future__ import annotations
import attrs
from typing import List, ClassVar
from .metadata import Metadata
from .platform import platform
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

        # Define static state
        self.add_defined("title")
        self.add_defined("description")
        self.add_defined("message")
        self.add_defined("tags")

        # Render message
        descriptor = self.metadata_export(exclude=["message"])
        self.message = helpers.safe_format(self.template, descriptor)

    # State

    message: str = attrs.field(init=False)
    """NOTE: add docs"""

    note: str
    """NOTE: add docs"""

    # Metadata

    metadata_type = "error"
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
    def metadata_specify(cls, *, type=None, property=None):
        if type:
            return platform.frictionless.system.select_Error(type)

    @classmethod
    def metadata_transform(cls, descriptor):
        super().metadata_transform(descriptor)

        # Class props
        descriptor.pop("title", None)
        descriptor.pop("description", None)
        descriptor.pop("tags", None)
        descriptor.pop("message", None)
