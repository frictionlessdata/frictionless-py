from __future__ import annotations
from typing import List
from ..metadata2 import Metadata2
from ..errors import InquiryError
from .validate import validate
from .task import InquiryTask


class Inquiry(Metadata2):
    """Inquiry representation."""

    validate = validate

    def __init__(self, *, tasks: List[InquiryTask]):
        self.tasks = tasks

    # Properties

    tasks: List[InquiryTask]
    """List of underlaying tasks"""

    # Convert

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = {
        "properties": {
            "tasks": {},
        }
    }

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors
