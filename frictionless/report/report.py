from __future__ import annotations
import attrs
from tabulate import tabulate
from typing import TYPE_CHECKING, List, Optional
from ..stats import Stats
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .task import ReportTask
from .. import settings

if TYPE_CHECKING:
    from ..resource import Resource


@attrs.define(kw_only=True)
class Report(Metadata):
    """Report representation.

    A class that stores the summary of the validation action.

    """

    # State

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Report.
    """

    description: Optional[str] = None
    """
    A brief description of the Detector.
    """

    valid: bool
    """
    Flag to specify if the data is valid or not.
    """

    stats: Stats
    """
    Additional statistics of the data as defined in Stats class.
    """

    warnings: List[str] = attrs.field(factory=list)
    """
    List of warnings raised while validating the data.
    """

    errors: List[Error] = attrs.field(factory=list)
    """
    List of errors raised while validating the data.
    """

    tasks: List[ReportTask] = attrs.field(factory=list)
    """
    List of task that were applied during data validation.
    """

    # Props

    @property
    def error(self):
        """Validation error (if there is only one)"""
        if self.stats.errors != 1:
            note = 'The "report.error" is available for single error reports'
            raise FrictionlessException(note)
        return self.tasks[0].error if self.tasks else self.errors[0]

    @property
    def task(self):
        """Validation task (if there is only one)"""
        if self.stats.tasks != 1:
            note = 'The "report.task" is available for single task reports'
            raise FrictionlessException(note)
        return self.tasks[0]

    # Flatten

    def flatten(self, spec=["taskNumber", "rowNumber", "fieldNumber", "type"]):
        """Flatten the report

        Parameters
            spec (str[]): flatten specification

        Returns:
            any[]: flatten report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error.to_descriptor())
            result.append([context.get(prop) for prop in spec])
        for count, task in enumerate(self.tasks, start=1):
            for error in task.errors:
                context = {"taskNumber": count, "taskNumber": count}
                context.update(error.to_descriptor())
                result.append([context.get(prop) for prop in spec])
        return result

    # Convert

    @staticmethod
    def from_validation(
        *,
        time: float,
        tasks: List[ReportTask] = [],
        errors: List[Error] = [],
        warnings: List[str] = [],
    ):
        """Create a report from a validation"""
        tasks = tasks.copy()
        errors = errors.copy()
        warnings = warnings.copy()
        error_count = len(errors) + sum(task.stats.errors or 0 for task in tasks)
        stats = Stats(
            tasks=len(tasks),
            errors=error_count,
            warnings=len(warnings),
            seconds=time,
        )
        return Report(
            valid=not error_count,
            stats=stats,
            warnings=warnings,
            errors=errors,
            tasks=tasks,
        )

    @staticmethod
    def from_validation_task(
        resource: Resource,
        *,
        time: float,
        labels: List[str] = [],
        errors: List[Error] = [],
        warnings: List[str] = [],
    ):
        """Create a report from a validation task"""
        errors = errors.copy()
        warnings = warnings.copy()
        task_stats = resource.stats.to_copy()
        task_stats.errors = len(errors)
        task_stats.warnings = len(warnings)
        task_stats.seconds = time
        report_stats = Stats(
            tasks=1,
            errors=len(errors),
            warnings=len(warnings),
            seconds=time,
        )
        return Report(
            valid=not errors,
            stats=report_stats,
            warnings=[],
            errors=[],
            tasks=[
                ReportTask(
                    valid=not errors,
                    name=resource.name,  # type: ignore
                    type=resource.type,  # type: ignore
                    place=resource.place,  # type: ignore
                    labels=labels,
                    stats=task_stats,
                    errors=errors,
                    warnings=warnings,
                )
            ],
        )

    @staticmethod
    def from_validation_reports(
        *,
        time: float,
        reports: List[Report],
    ):
        """Create a report from a set of validation reports"""
        tasks = []
        errors = []
        warnings = []
        for report in reports:
            tasks.extend(report.tasks)
            errors.extend(report.errors)
            warnings.extend(report.warnings)
        return Report.from_validation(
            time=time,
            warnings=warnings,
            errors=errors,
            tasks=tasks,
        )

    # TODO: move to ReportTask
    def to_summary(self):
        """Summary of the report

        Returns:
            str: validation report
        """

        validation_content = ""
        for task in self.tasks:
            prefix = "valid" if task.valid else "invalid"
            suffix = "" if task.tabular else "(non-tabular)"
            validation_content += f"\n# {'-'*len(prefix)}"
            validation_content += f"\n# {prefix}: {task.place} {suffix}"
            validation_content += f"\n# {'-'*len(prefix)}"
            error_content = []
            if task.errors:
                for error in task.errors:
                    error_descriptor = error.to_descriptor()
                    error_content.append(
                        [
                            error_descriptor.get("rowNumber", ""),
                            error_descriptor.get("fieldNumber", ""),
                            error.type,
                            error.message,
                        ]
                    )
            # Validate
            validation_content += "\n\n"
            validation_content += "## Summary "
            validation_content += "\n\n"
            validation_content += task.to_summary()
            validation_content += "\n\n"
            # errors
            if task.errors:
                validation_content += "## Errors "
                validation_content += "\n\n"
                validation_content += str(
                    tabulate(
                        error_content,
                        headers=["Row", "Field", "Type", "Message"],
                        tablefmt="grid",
                        # TODO: create based on the actual users's terminal width?
                        maxcolwidths=[5, 5, 20, 90],  # type: ignore
                    )
                )
                validation_content += "\n\n"
        return validation_content

    # Metadata

    metadata_type = "report"
    metadata_Error = ReportError
    metadata_profile = {
        "type": "object",
        "required": ["valid", "stats", "warnings", "errors", "tasks"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "valid": {"type": "boolean"},
            "stats": {"type": "object"},
            "warnings": {"type": "array"},
            "errors": {"type": "array"},
            "tasks": {"type": "array"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "stats":
            return Stats
        elif property == "errors":
            return Error
        elif property == "tasks":
            return ReportTask

    # TODO: validate valid/errors count
