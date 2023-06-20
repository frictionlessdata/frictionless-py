from __future__ import annotations

from typing import Any, ClassVar, List, Optional, Type

import attrs

from .. import helpers, types
from ..metadata import Metadata
from ..platform import platform

# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.


@attrs.define(kw_only=True, repr=False)
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

    message: str = attrs.field(init=False)
    """
    A human readable informative comprehensive description of the error. It can be set to any custom text.
    If not set, default description is more comprehensive with error type, message and reasons included.
    """

    note: str
    """
    A short human readable description of the error. It can be set to any custom text.
    """

    def __attrs_post_init__(self):
        # Define static state
        self.add_defined("title")
        self.add_defined("description")
        self.add_defined("message")
        self.add_defined("tags")

        # Render message
        descriptor = self.metadata_export(exclude=["message"])
        self.message = helpers.safe_format(self.template, descriptor)

        super().__attrs_post_init__()

    # List

    @classmethod
    def list_children(
        cls, *, root: bool = False, exclude: Optional[List[Type[Error]]] = None
    ) -> List[Type[Error]]:
        children: List[Type[Error]] = []
        for item in vars(platform.frictionless_errors).values():
            if isinstance(item, type) and issubclass(item, cls):
                if not root and item is cls:
                    continue
                if exclude and issubclass(item, tuple(exclude)):  # type: ignore
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
    def metadata_select_class(cls, type: Optional[str]):
        return platform.frictionless.system.select_error_class(type)

    @classmethod
    def metadata_import(cls, descriptor: types.IDescriptor, **options: Any):  # type: ignore
        # Class props
        descriptor.pop("title", None)
        descriptor.pop("description", None)
        descriptor.pop("tags", None)
        descriptor.pop("message", None)

        return super().metadata_import(descriptor, **options)
