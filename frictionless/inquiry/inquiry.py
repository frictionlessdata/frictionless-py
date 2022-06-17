from __future__ import annotations
from copy import deepcopy
from typing import TYPE_CHECKING, List
from ..metadata2 import Metadata2
from ..errors import InquiryError
from .validate import validate
from .task import InquiryTask
from .. import settings

if TYPE_CHECKING:
    from ..interfaces import IDescriptor, IPlainDescriptor


class Inquiry(Metadata2):
    """Inquiry representation."""

    validate = validate

    def __init__(self, *, tasks: List[InquiryTask]):
        self.tasks = tasks

    # Properties

    tasks: List[InquiryTask]
    """List of underlaying tasks"""

    # Convert

    convert_properties = [
        "tasks",
    ]

    @classmethod
    def from_descriptor(cls, descriptor):
        metadata = super().from_descriptor(descriptor)
        metadata.tasks = [InquiryTask.from_descriptor(task) for task in metadata.tasks]  # type: ignore
        return metadata

    def to_descriptor(self):
        descriptor = super().to_descriptor()
        descriptor["tasks"] = [task.to_descriptor() for task in self.tasks]
        return descriptor

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = deepcopy(settings.INQUIRY_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors
