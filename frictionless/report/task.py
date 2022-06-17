from __future__ import annotations
from importlib import import_module
from tabulate import tabulate
from typing import Optional, List
from ..metadata2 import Metadata2
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .. import settings
from .. import helpers


class ReportTask(Metadata2):
    """Report task representation."""

    def __init__(
        self,
        valid: bool,
        name: str,
        place: str,
        tabular: bool,
        stats: dict,
        scope: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[Error]] = None,
    ):
        self.valid = valid
        self.name = name
        self.place = place
        self.tabular = tabular
        self.stats = stats
        self.scope = scope or []
        self.warnings = warnings or []
        self.errors = errors or []

    # Properties

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

    scope: List[str]
    """# TODO: add docs"""

    warnings: List[str]
    """# TODO: add docs"""

    errors: List[Error]
    """# TODO: add docs"""

    @property
    def error(self):
        """
        Returns:
            Error: validation error if there is only one

        Raises:
            FrictionlessException: if more than one errors
        """
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

    convert_properties = [
        "valid",
        "name",
        "place",
        "tabular",
        "stats",
        "scope",
        "warnings",
        "errors",
    ]

    # TODO: why system is circular dependency?
    @classmethod
    def from_descriptor(cls, descriptor):
        system = import_module("frictionless").system
        metadata = super().from_descriptor(descriptor)
        metadata.errors = [system.create_error(error) for error in metadata.errors]
        return metadata

    # TODO: rebase on to_descriptor
    def to_descriptor(self):
        descriptor = super().to_descriptor()
        descriptor["errors"] = [error.to_dict() for error in self.errors]
        return descriptor

    def to_summary(self) -> str:
        """Generate summary for validation task"

        Returns:
            str: validation summary
        """
        # Prepare error lists and last row checked(in case of partial validation)
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

    metadata_Error = ReportError
    metadata_profile = settings.REPORT_PROFILE["properties"]["tasks"]["items"]

    # TODO: validate valid/errors count
    # TODO: validate stats when the class is added
    # TODO: validate errors when metadata is reworked
    def metadata_validate(self):
        yield from super().metadata_validate()
