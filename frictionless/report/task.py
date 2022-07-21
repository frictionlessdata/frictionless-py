from __future__ import annotations
import attrs
import humanize
from typing import List
from tabulate import tabulate
from ..stats import Stats
from ..metadata import Metadata
from ..exception import FrictionlessException
from ..errors import ReportTaskError
from ..error import Error
from .. import settings


@attrs.define(kw_only=True)
class ReportTask(Metadata):
    """Report task representation."""

    # State

    valid: bool
    """# TODO: add docs"""

    name: str
    """# TODO: add docs"""

    type: str
    """# TODO: add docs"""

    place: str
    """# TODO: add docs"""

    stats: Stats
    """# TODO: add docs"""

    scope: List[str] = attrs.field(factory=list)
    """# TODO: add docs"""

    warnings: List[str] = attrs.field(factory=list)
    """# TODO: add docs"""

    errors: List[Error] = attrs.field(factory=list)
    """# TODO: add docs"""

    # Props

    @property
    def error(self):
        """Validation error if there is only one"""
        if len(self.errors) != 1:
            error = Error(note='The "task.error" is available for single error tasks')
            raise FrictionlessException(error)
        return self.errors[0]

    @property
    def tabular(self) -> bool:
        """Whether task's resource is tabular"""
        return self.type == "table"

    # Flatten

    def flatten(self, spec=["rowNumber", "fieldNumber", "type"]):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten task report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error.to_descriptor())
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
            error_title = f"{error.title}"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
        size = self.stats.bytes
        content = [
            ["File Place", self.place],
            ["File Size", humanize.naturalsize(size) if size else "(file not found)"],
            ["Total Time", f"{self.stats.seconds} Seconds"],
            ["Rows Checked", self.stats.rows],
        ]
        if error_list:
            content.append(["Total Errors", sum(error_list.values())])
        for type, count in error_list.items():
            content.append([type, count])
        output = ""
        for warning in self.warnings:
            output += f"> {warning}\n\n"
        output += tabulate(content, headers=["Name", "Value"], tablefmt="grid")
        return output

    # Metadata

    metadata_type = "report-task"
    metadata_Error = ReportTaskError
    metadata_Types = dict(stats=Stats, errors=Error)
    metadata_profile = {
        "type": "object",
        "required": [
            "valid",
            "name",
            "type",
            "place",
            "stats",
            "scope",
            "warnings",
            "errors",
        ],
        "properties": {
            "valid": {"type": "boolean"},
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "place": {"type": "string"},
            "stats": {"type": "object"},
            "scope": {"type": "array"},
            "warnings": {"type": "array"},
            "errors": {"type": "array"},
        },
    }

    # TODO: validate valid/errors count
    # TODO: validate stats when the class is added
    # TODO: validate errors when metadata is reworked
    def metadata_validate(self):
        yield from super().metadata_validate()
