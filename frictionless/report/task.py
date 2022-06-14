from __future__ import annotations
from tabulate import tabulate
from importlib import import_module
from typing import TYPE_CHECKING, Optional, List
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


class ReportTask(Metadata):
    """Report task representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import ReportTask`

    Parameters:
        descriptor? (str|dict): schema descriptor
        resource? (Resource): resource
        time (float): validation time
        scope (str[]): validation scope
        errors (Error[]): validation errors
        warning (str): validation warning

    # Raises
        FrictionlessException: raise any error that occurs during the process

    """

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
        scope = scope or []
        errors = errors or []
        self.setinitial("valid", valid)
        self.setinitial("name", name)
        self.setinitial("place", place)
        self.setinitial("tabular", tabular)
        self.setinitial("stats", stats)
        self.setinitial("scope", scope)
        self.setinitial("warnings", warnings)
        self.setinitial("errors", errors)
        super().__init__()

    @property
    def valid(self) -> bool:
        """
        Returns:
            bool: validation result
        """
        return self.get("valid")  # type: ignore

    @property
    def name(self):
        """
        Returns:
            str: name
        """
        return self.get("name")

    @property
    def place(self):
        """
        Returns:
            str: place
        """
        return self.get("place")

    @property
    def tabular(self):
        """
        Returns:
            bool: tabular
        """
        return self.get("tabular")

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self.get("stats", {})

    @property
    def scope(self):
        """
        Returns:
            str[]: validation scope
        """
        return self.get("scope", [])

    @property
    def warnings(self):
        """
        Returns:
            bool: if validation warning
        """
        return self.get("warnings", [])

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self.get("errors", [])

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

    # Import/Export

    @staticmethod
    def from_descriptor(descriptor: IDescriptor):
        metadata = Metadata(descriptor)
        system = import_module("frictionless").system
        errors = [system.create_error(error) for error in metadata.get("errors", [])]
        return ReportTask(
            valid=metadata.get("valid"),  # type: ignore
            name=metadata.get("name"),  # type: ignore
            place=metadata.get("place"),  # type: ignore
            tabular=metadata.get("tabular"),  # type: ignore
            stats=metadata.get("stats"),  # type: ignore
            scope=metadata.get("scope"),  # type: ignore
            warning=metadata.get("warning"),  # type: ignore
            errors=errors,
        )

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

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Stats
        # TODO: validate valid/errors count
        # TODO: validate stats when the class is added

        # Errors
        # TODO: validate errors when metadata is reworked
