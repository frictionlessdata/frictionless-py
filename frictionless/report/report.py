from __future__ import annotations
import textwrap
from copy import deepcopy
from tabulate import tabulate
from importlib import import_module
from typing import TYPE_CHECKING, Optional, List
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .validate import validate
from .task import ReportTask
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor
    from ..resource import Resource


# NOTE:
# We can allow some Report/ReportTask constructor kwargs be None
# We need to review how we validate Report/ReportTask (strict mode is disabled)


class Report(Metadata):
    """Report representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Report`

    Parameters:
        descriptor? (str|dict): report descriptor
        time (float): validation time
        errors (Error[]): validation errors
        tasks (ReportTask[]): validation tasks

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    validate = validate

    def __init__(
        self,
        version: str,
        valid: bool,
        stats: dict,
        tasks: Optional[List[ReportTask]] = None,
        errors: Optional[List[Error]] = None,
        warning: Optional[str] = None,
    ):
        self.setinitial("version", version)
        self.setinitial("valid", valid)
        self.setinitial("stats", stats)
        self.setinitial("tasks", tasks)
        self.setinitial("errors", errors)
        self.setinitial("warning", warning)
        super().__init__()

    @property
    def version(self):
        """
        Returns:
            str: frictionless version
        """
        return self.get("version")

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self.get("valid")

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self.get("stats", {})

    @property
    def warning(self):
        """
        Returns:
            Error[]: validation warning
        """
        return self.get("warning")

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self.get("errors", [])

    @property
    def tasks(self):
        """
        Returns:
            ReportTask[]: validation tasks
        """
        return self.get("tasks", [])

    @property
    def task(self):
        """
        Returns:
            ReportTask: validation task (if there is only one)

        Raises:
            FrictionlessException: if there are more that 1 task
        """
        if len(self.tasks) != 1:
            error = Error(note='The "report.task" is available for single task reports')
            raise FrictionlessException(error)
        return self.tasks[0]

    # Expand

    def expand(self):
        """Expand metadata"""
        for task in self.tasks:
            task.expand()

    # Flatten

    def flatten(self, spec=["taskPosition", "rowPosition", "fieldPosition", "code"]):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        for count, task in enumerate(self.tasks, start=1):
            for error in task.errors:
                context = {"taskNumber": count, "taskPosition": count}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result

    # Export/Import

    @staticmethod
    def from_descriptor(descriptor: IDescriptor):
        metadata = Metadata(descriptor)
        system = import_module("frictionless").system
        errors = [system.create_error(error) for error in metadata.get("errors", [])]
        tasks = [ReportTask.from_descriptor(task) for task in metadata.get("tasks", [])]
        return Report(
            version=metadata.get("version"),  # type: ignore
            valid=metadata.get("valid"),  # type: ignore
            stats=metadata.get("stats"),  # type: ignore
            scope=metadata.get("scope"),  # type: ignore
            warning=metadata.get("warning"),  # type: ignore
            errors=errors,
            tasks=tasks,
        )

    @staticmethod
    def from_validation(
        time: float,
        tasks: Optional[List[ReportTask]] = None,
        errors: Optional[List[Error]] = None,
        warning: Optional[str] = None,
    ):
        """Create a report from a validation"""
        tasks = tasks or []
        errors = errors or []
        error_count = len(errors) + sum(task.stats["errors"] for task in tasks)
        stats = {"time": time, "tasks": len(tasks), "errors": error_count}
        return Report(
            version=settings.VERSION,
            valid=not error_count,
            stats=stats,
            tasks=tasks,
            errors=errors,
            warning=warning,
        )

    @staticmethod
    def from_validation_task(
        resource: Resource,
        *,
        time: float,
        scope: Optional[List[str]] = None,
        errors: Optional[List[Error]] = None,
        warning: Optional[str] = None,
    ):
        """Create a report from a validation task"""
        scope = scope or []
        errors = errors or []
        task_stats = helpers.copy_merge(resource.stats, time=time, errors=len(errors))
        report_stats = {"time": time, "tasks": 1, "errors": len(errors)}
        return Report(
            version=settings.VERSION,
            valid=not errors,
            stats=report_stats,
            errors=[],
            tasks=[
                ReportTask(
                    valid=not errors,
                    name=resource.name,  # type: ignore
                    place=resource.place,  # type: ignore
                    tabular=resource.tabular,  # type: ignore
                    stats=task_stats,
                    scope=scope,
                    warning=warning,
                    errors=errors,
                )
            ],
        )

    def to_summary(self):
        """Summary of the report

        Returns:
            str: validation report
        """

        validation_content = ""
        for task in self.tasks:
            prefix = "valid" if task.valid else "invalid"
            suffix = "" if task.tabular else "(non-tabular)"
            source = task.path or task.name
            # for zipped resources append file name
            if task.innerpath:
                source = f"{source} => {task.resource.innerpath}"
            validation_content += f"\n# {'-'*len(prefix)}"
            validation_content += f"\n# {prefix}: {source} {suffix}"
            validation_content += f"\n# {'-'*len(prefix)}"
            error_content = []
            if task.errors:
                for error in task.errors:
                    error_content.append(
                        [
                            error.get("rowPosition", ""),
                            error.get("fieldPosition", ""),
                            error.code,
                            error.message,
                        ]
                    )
            # Validate
            error_content = wrap_text_to_colwidths(error_content)
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
                    )
                )
                validation_content += "\n\n"
        return validation_content

    # Metadata

    metadata_Error = ReportError
    metadata_profile = deepcopy(settings.REPORT_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Stats
        # TODO: validate valid/errors count
        # TODO: validate stats when the class is added

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors

        # Errors
        # TODO: validate errors when metadata is reworked


# TODO: Temporary function to use with tabulate  tabulate 0.8.9 does not support text wrap
def wrap_text_to_colwidths(list_of_lists: List, colwidths: List = [5, 5, 10, 50]) -> List:
    """Create new list with wrapped text with different column width.
    Args:
        list_of_lists (List): List of lines
        colwidths (List): width for each column

    Returns:
        List: list of lines with wrapped text

    """
    result = []
    for row in list_of_lists:
        new_row = []
        for cell, width in zip(row, colwidths):
            cell = str(cell)
            wrapped = textwrap.wrap(cell, width=width)
            new_row.append("\n".join(wrapped))
        result.append(new_row)
    return result
