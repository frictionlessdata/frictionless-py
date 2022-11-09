from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, Optional, List
from multiprocessing import Pool
from ..platform import platform
from ..metadata import Metadata
from ..errors import InquiryError
from .task import InquiryTask
from ..report import Report
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


@attrs.define
class Inquiry(Metadata):
    """Inquiry representation."""

    # State

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
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

    def validate(self, *, parallel=False):
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
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tasks": {"type": "array", "items": {"type": "object"}},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "tasks":
            return InquiryTask


# Internal


def validate_parallel(descriptor: IDescriptor) -> IDescriptor:
    task = platform.frictionless.InquiryTask.from_descriptor(descriptor)
    report = task.validate()
    return report.to_descriptor()
