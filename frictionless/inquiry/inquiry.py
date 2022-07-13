from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, Optional, List
from importlib import import_module
from multiprocessing import Pool
from ..metadata import Metadata
from ..errors import InquiryError
from .task import InquiryTask
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


@attrs.define
class Inquiry(Metadata):
    """Inquiry representation."""

    # State

    name: Optional[str] = None
    """# TODO: add docs"""

    title: Optional[str] = None
    """TODO: add docs"""

    description: Optional[str] = None
    """TODO: add docs"""

    tasks: List[InquiryTask] = attrs.field(factory=list)
    """List of underlaying tasks"""

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

        # Validate inquiry
        if self.metadata_errors:
            errors = self.metadata_errors
            return Report.from_validation(time=timer.time, errors=errors)

        # Validate sequential
        if not parallel:
            for task in self.tasks:
                report = task.validate(metadata=False)
                reports.append(report)

        # Validate parallel
        else:
            with Pool() as pool:
                task_descriptors = [task.to_descriptor() for task in self.tasks]
                report_descriptors = pool.map(validate_parallel, task_descriptors)
                for report_descriptor in report_descriptors:
                    reports.append(Report.from_descriptor(report_descriptor))

        # Return report
        return Report.from_validation_reports(
            time=timer.time,
            reports=reports,
        )

    # Metadata

    metadata_Error = InquiryError
    metadata_Types = dict(tasks=InquiryTask)
    metadata_profile = {
        "properties": {
            "name": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tasks": {"type": "array"},
        }
    }

    def metadata_validate(self):
        yield from super().metadata_validate()
        for task in self.tasks:
            yield from task.metadata_errors


# Internal


def validate_parallel(descriptor: IDescriptor) -> IDescriptor:
    InquiryTask = import_module("frictionless").InquiryTask
    task = InquiryTask.from_descriptor(descriptor)
    report = task.validate(metadata=False)
    return report.to_descriptor()
