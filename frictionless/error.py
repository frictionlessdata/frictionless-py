from __future__ import annotations
import attrs
from typing import List, ClassVar, Optional, Type
from .metadata import Metadata
from .platform import platform
from . import helpers


# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.


@attrs.define(kw_only=True)
class Error(Metadata):
    """Error representation.

    It is a baseclass from which other subclasses of errors are inherited or
    derived from.
    """

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
    """
    A human readable informative comprehensive description of the error. It can be set to any custom text. 
    If not set, default description is more comprehensive with error type, message and reasons included.
    """

    note: str
    """
    A short human readable description of the error. It can be set to any custom text.
    """

    # List

    @classmethod
    def list_children(
        cls, *, root: bool = False, exclude: Optional[List[Type[Error]]] = None
    ) -> List[Type[Error]]:
        children = []
        for item in vars(platform.frictionless_errors).values():
            if isinstance(item, type) and issubclass(item, cls):
                if not root and item is cls:
                    continue
                if exclude and issubclass(item, tuple(exclude)):
                    continue
                children.append(item)
        return children

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
        if type is not None:
            return platform.frictionless.system.select_Error(type)

    @classmethod
    def metadata_import(cls, descriptor, **options):

        # Class props
        descriptor.pop("title", None)
        descriptor.pop("description", None)
        descriptor.pop("tags", None)
        descriptor.pop("message", None)

        return super().metadata_import(descriptor, **options)
