from __future__ import annotations
from tabulate import tabulate
from typing import Optional, List, Any
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .. import settings
from .. import helpers


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
        descriptor: Optional[Any] = None,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        innerpath: Optional[str] = None,
        memory: Optional[bool] = None,
        tabular: Optional[bool] = None,
        stats: Optional[dict] = None,
        time: Optional[float] = None,
        scope: Optional[List[str]] = None,
        errors: Optional[List[Error]] = None,
        warning: Optional[str] = None,
    ):

        # Store provided
        self.setinitial("name", name)
        self.setinitial("path", path)
        self.setinitial("innerpath", innerpath)
        self.setinitial("memory", memory)
        self.setinitial("tabular", tabular)
        self.setinitial("time", time)
        self.setinitial("scope", scope)
        self.setinitial("errors", errors)
        self.setinitial("warning", warning)
        super().__init__(descriptor)

        # Store computed
        merged_stats = {"errors": len(self.errors)}
        if stats:
            merged_stats.update(stats)
        self.setinitial("stats", merged_stats)
        self.setinitial("valid", not self.errors)

    @property
    def name(self):
        """
        Returns:
            str: name
        """
        return self.get("name")

    @property
    def path(self):
        """
        Returns:
            str: path
        """
        return self.get("path")

    @property
    def innerpath(self):
        """
        Returns:
            str: innerpath
        """
        return self.get("innerpath")

    @property
    def memory(self):
        """
        Returns:
            bool: memory
        """
        return self.get("memory")

    @property
    def tabular(self):
        """
        Returns:
            bool: tabular
        """
        return self.get("tabular")

    @property
    def time(self):
        """
        Returns:
            float: validation time
        """
        return self.get("time")

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self.get("valid")

    @property
    def scope(self):
        """
        Returns:
            str[]: validation scope
        """
        return self.get("scope", [])

    @property
    def warning(self):
        """
        Returns:
            bool: if validation warning
        """
        return self.get("warning")

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self.get("stats", {})

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

    # Export/Import

    def to_summary(self) -> str:
        """Generate summary for validation task"

        Returns:
            str: validation summary
        """
        source = self.path or self.name
        # For zipped resources append file name
        if self.innerpath:
            source = f"{source} => {self.innerpath}"
        # Prepare error lists and last row checked(in case of partial validation)
        error_list = {}
        for error in self.errors:
            error_title = f"{error.name} ({error.code})"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
        content = [
            ["File name", source],
            ["File size", helpers.format_bytes(self.stats["bytes"])],
            ["Total Time", self.time],
            ["Rows Checked", self.stats["rows"]],
        ]
        if error_list:
            content.append(["Total Errors", sum(error_list.values())])
        for code, count in error_list.items():
            content.append([code, count])
        output = ""
        if self.warning:
            output += f">> {self.warning}\n\n"
        output += tabulate(content, headers=["Name", "Value"], tablefmt="grid")
        return output

    # Metadata

    metadata_Error = ReportError
    metadata_profile = settings.REPORT_PROFILE["properties"]["tasks"]["items"]
