from __future__ import annotations
from copy import deepcopy
from typing import TYPE_CHECKING, List
from ..metadata2 import Metadata2
from ..errors import InquiryError
from .validate import validate
from .task import InquiryTask
from .. import settings

if TYPE_CHECKING:
    from ..interfaces import IDescriptor, IResolvedDescriptor


class Inquiry(Metadata2):
    """Inquiry representation."""

    validate = validate

    def __init__(self, *, tasks: List[InquiryTask]):
        self.tasks = tasks

    tasks: List[InquiryTask]
    """List of underlaying tasks"""

    # Export/Import

    @classmethod
    def from_descriptor(cls, descriptor: IDescriptor):
        mapping = cls.metadata_extract(descriptor)
        tasks = [InquiryTask.from_descriptor(task) for task in mapping.get("tasks", [])]
        return Inquiry(tasks=tasks)

    def to_descriptor(self) -> IResolvedDescriptor:
        tasks = [task.to_descriptor() for task in self.tasks]
        descriptor: IResolvedDescriptor = dict(tasks=tasks)
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
