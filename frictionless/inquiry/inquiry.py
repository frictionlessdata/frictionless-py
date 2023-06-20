from __future__ import annotations

from multiprocessing import Pool
from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

import attrs

from .. import helpers, settings
from ..errors import InquiryError
from ..metadata import Metadata
from ..platform import platform
from ..report import Report
from .task import InquiryTask

if TYPE_CHECKING:
    from .. import types


@attrs.define(kw_only=True, repr=False)
class Inquiry(Metadata):
    """Inquiry representation."""

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: ClassVar[Union[str, None]] = None
    """
    Type of the object
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Inquiry.
    """

    description: Optional[str] = None
    """
    A brief description of the Inquiry.
    """

    tasks: List[InquiryTask] = attrs.field(factory=list)
    """
    List of underlaying task to be validated.
    """

    # Validate

    def validate(self, *, parallel: bool = False):
        """Validate inquiry

        Parameters:
            parallel? (bool): enable multiprocessing

        Returns:
            Report: validation report
        """

        # Create state
        timer = helpers.Timer()
        reports: List[Report] = []

        # Validate sequential
        if not parallel:
            for task in self.tasks:
                report = task.validate()
                reports.append(report)

        # Validate parallel
        else:
            with Pool() as pool:
                task_descriptors = [task.to_descriptor() for task in self.tasks]
                report_descriptors = pool.map(validate_parallel, task_descriptors)
                for report_descriptor in report_descriptors:
                    reports.append(Report.from_descriptor(report_descriptor))

        # Return report
        report = Report.from_validation_reports(time=timer.time, reports=reports)
        report.name = self.name
        report.title = self.title
        report.description = self.description
        return report

    # Metadata

    metadata_type = "inquiry"
    metadata_Error = InquiryError
    metadata_profile = {
        "type": "object",
        "required": ["tasks"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tasks": {"type": "array", "items": {"type": "object"}},
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "tasks":
            return InquiryTask


# Internal


def validate_parallel(descriptor: types.IDescriptor) -> types.IDescriptor:
    task = platform.frictionless.InquiryTask.from_descriptor(descriptor)
    report = task.validate()
    return report.to_descriptor()
