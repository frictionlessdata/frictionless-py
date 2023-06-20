from __future__ import annotations

from typing import Any, Dict, List, Optional

import attrs
import humanize
from tabulate import tabulate

from .. import settings
from ..error import Error
from ..errors import ReportTaskError
from ..exception import FrictionlessException
from ..metadata import Metadata
from . import types


@attrs.define(kw_only=True, repr=False)
class ReportTask(Metadata):
    """Report task representation."""

    name: str
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: Optional[str]
    """
    Sets the property tabular to True if the type is "table".
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

    place: str
    """
    Specifies the place of the file. For example: "<memory>", "data/table.csv" etc.
    """

    labels: List[str]
    """
    List of labels of the task resource.
    """

    stats: types.IReportTaskStats
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

    def flatten(self, spec: List[str] = ["rowNumber", "fieldNumber", "type"]):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten task report
        """
        result: List[Any] = []
        for error in self.errors:
            context: Dict[str, Any] = {}
            context.update(error.to_descriptor())
            result.append([context.get(prop) for prop in spec])
        return result

    # Convert

    def to_summary(self) -> str:
        """Generate summary for validation task"

        Returns:
            str: validation summary
        """
        error_list: Dict[str, Any] = {}
        for error in self.errors:
            error_title = f"{error.title}"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
        size = self.stats.get("bytes")
        content = [
            ["File Place", self.place],
            ["File Size", humanize.naturalsize(size) if size else "(file not found)"],
            ["Total Time", f"{self.stats.get('seconds')} Seconds"],
            ["Rows Checked", self.stats.get("rows")],
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
    metadata_profile = {
        "type": "object",
        "required": [
            "valid",
            "name",
            "place",
            "stats",
            "warnings",
            "errors",
        ],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "valid": {"type": "boolean"},
            "place": {"type": "string"},
            "labels": {"type": "array", "arrayItem": {"type": "string"}},
            "stats": {"type": "object"},
            "warnings": {"type": "array", "arrayItem": {"type": "string"}},
            "errors": {"type": "array", "arrayItem": {"type": "object"}},
        },
    }

    @classmethod
    def metadata_select_class(cls, type: Optional[str]):
        return ReportTask

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "errors":
            return Error

    # TODO: validate valid/errors count
