from __future__ import annotations
from typing import TYPE_CHECKING, List
from importlib import import_module
from multiprocessing import Pool
from dataclasses import dataclass, field
from ..metadata2 import Metadata2
from ..errors import InquiryError
from .task import InquiryTask
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


@dataclass
class Inquiry(Metadata2):
    """Inquiry representation."""

    # Properties

    tasks: List[InquiryTask] = field(default_factory=list)
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
    metadata_profile = {
        "properties": {
            "tasks": {},
        }
    }

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(tasks=InquiryTask)

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
