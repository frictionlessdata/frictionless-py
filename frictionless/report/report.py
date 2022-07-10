from __future__ import annotations
from tabulate import tabulate
from typing import TYPE_CHECKING, List
from dataclasses import dataclass, field
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .task import ReportTask
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..resource import Resource


@dataclass
class Report(Metadata):
    """Report representation."""

    # State

    valid: bool
    """# TODO: add docs"""

    stats: dict
    """# TODO: add docs"""

    warnings: List[str] = field(default_factory=list)
    """# TODO: add docs"""

    errors: List[Error] = field(default_factory=list)
    """# TODO: add docs"""

    tasks: List[ReportTask] = field(default_factory=list)
    """# TODO: add docs"""

    # Props

    @property
    def task(self):
        """Validation task (if there is only one)"""
        if len(self.tasks) != 1:
            error = Error(note='The "report.task" is available for single task reports')
            raise FrictionlessException(error)
        return self.tasks[0]

    # Validate

    def validate(self):
        timer = helpers.Timer()
        errors = self.metadata_errors
        return Report.from_validation(time=timer.time, errors=errors)

    # Flatten

    def flatten(self, spec=["taskNumber", "rowNumber", "fieldNumber", "code"]):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

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
        error_count = len(errors) + sum(task.stats["errors"] for task in tasks)
        stats = {"time": time, "tasks": len(tasks), "errors": error_count}
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
        scope: List[str] = [],
        errors: List[Error] = [],
        warnings: List[str] = [],
    ):
        """Create a report from a validation task"""
        scope = scope.copy()
        errors = errors.copy()
        warnings = warnings.copy()
        task_stats = helpers.copy_merge(resource.stats, time=time, errors=len(errors))
        report_stats = {"time": time, "tasks": 1, "errors": len(errors)}
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
                    stats=task_stats,
                    scope=scope,
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
                            error.code,
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
                        headers=["row", "field", "code", "message"],
                        tablefmt="grid",
                        # TODO: create based on the actual users's terminal width?
                        maxcolwidths=[5, 5, 20, 90],
                    )
                )
                validation_content += "\n\n"
        return validation_content

    # Metadata

    metadata_Error = ReportError
    metadata_profile = {
        "properties": {
            "valid": {},
            "stats": {},
            "warnings": {},
            "errors": {},
            "tasks": {},
        }
    }

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(tasks=ReportTask)

    # TODO: validate valid/errors count
    # TODO: validate stats when the class is added
    # TODO: validate errors when metadata is reworked
    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors
