from __future__ import annotations
from typing import List
from tabulate import tabulate
from dataclasses import dataclass, field
from ..metadata import Metadata
from ..exception import FrictionlessException
from ..errors import Error, ReportTaskError
from .. import helpers


@dataclass
class ReportTask(Metadata):
    """Report task representation."""

    # State

    valid: bool
    """# TODO: add docs"""

    name: str
    """# TODO: add docs"""

    place: str
    """# TODO: add docs"""

    tabular: bool
    """# TODO: add docs"""

    stats: dict
    """# TODO: add docs"""

    scope: List[str] = field(default_factory=list)
    """# TODO: add docs"""

    warnings: List[str] = field(default_factory=list)
    """# TODO: add docs"""

    errors: List[Error] = field(default_factory=list)
    """# TODO: add docs"""

    # Props

    @property
    def error(self):
        """Validation error if there is only one"""
        if len(self.errors) != 1:
            error = Error(note='The "task.error" is available for single error tasks')
            raise FrictionlessException(error)
        return self.errors[0]

    # Flatten

    def flatten(self, spec=["rowPosition", "fieldPosition", "code"]):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten task report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        return result

    # Convert

    def to_summary(self) -> str:
        """Generate summary for validation task"

        Returns:
            str: validation summary
        """
        error_list = {}
        for error in self.errors:
            error_title = f"{error.name} ({error.code})"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
        content = [
            ["File place", self.place],
            ["File size", helpers.format_bytes(self.stats["bytes"])],
            ["Total Time", self.stats.get("time")],
            ["Rows Checked", self.stats.get("rows")],
        ]
        if error_list:
            content.append(["Total Errors", sum(error_list.values())])
        for code, count in error_list.items():
            content.append([code, count])
        output = ""
        for warning in self.warnings:
            output += f">> {warning}\n\n"
        output += tabulate(content, headers=["Name", "Value"], tablefmt="grid")
        return output

    # Metadata

    metadata_Error = ReportTaskError
    metadata_profile = {
        "properties": {
            "valid": {},
            "name": {},
            "place": {},
            "tabular": {},
            "stats": {},
            "scope": {},
            "warnings": {},
            "errors": {},
        }
    }

    # TODO: validate valid/errors count
    # TODO: validate stats when the class is added
    # TODO: validate errors when metadata is reworked
    def metadata_validate(self):
        yield from super().metadata_validate()
