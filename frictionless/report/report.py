import functools
from copy import deepcopy
from importlib import import_module
from tabulate import tabulate
from ..metadata import Metadata
from ..errors import Error, TaskError, ReportError
from ..exception import FrictionlessException
from .validate import validate
from .. import settings
from .. import helpers


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

    def __init__(self, descriptor=None, *, time=None, errors=None, tasks=None):
        # Store provided
        self.setinitial("version", settings.VERSION)
        self.setinitial("time", time)
        self.setinitial("errors", errors)
        self.setinitial("tasks", tasks)
        super().__init__(descriptor)

        # Store computed
        error_count = len(self.errors) + sum(task.stats["errors"] for task in self.tasks)
        self.setinitial("stats", {"errors": error_count, "tasks": len(self.tasks)})
        self.setinitial("valid", not error_count)

    @property
    def version(self):
        """
        Returns:
            str: frictionless version
        """
        return self["version"]

    @property
    def time(self):
        """
        Returns:
            float: validation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self["valid"]

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self["stats"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self["errors"]

    @property
    def tasks(self):
        """
        Returns:
            ReportTask[]: validation tasks
        """
        return self["tasks"]

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

    # Import/Export

    @staticmethod
    def from_validate(validate):
        """Validate function wrapper

        Parameters:
            validate (func): validate

        Returns:
            func: wrapped validate
        """

        @functools.wraps(validate)
        def wrapper(*args, **kwargs):
            timer = helpers.Timer()
            try:
                return validate(*args, **kwargs)
            except Exception as exception:
                error = TaskError(note=str(exception))
                if isinstance(exception, FrictionlessException):
                    error = exception.error
                return Report(time=timer.time, errors=[error], tasks=[])

        return wrapper

    # Summary

    def to_summary(self):
        """Summary of the report

        Returns:
            str: validation report
        """

        validation_content = ""
        for task in self.tasks:
            tabular = task.resource.profile == "tabular-data-resource"
            prefix = "valid" if task.valid else "invalid"
            suffix = "" if tabular else "(non-tabular)"
            source = task.resource.path or task.resource.name
            # for zipped resources append file name
            if task.resource.innerpath:
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
            validation_content += "\n\n"
            validation_content += "## Summary "
            validation_content += "\n\n"
            if task.partial:
                validation_content += (
                    "The document was partially validated because of one of the limits\n"
                )
                validation_content += "* limit errors \n"
                validation_content += "* memory Limit"
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
                        maxcolwidths=[5, 5, 10, 50],
                    )
                )
                validation_content += "\n\n"

        return validation_content

    # Metadata

    metadata_Error = ReportError
    metadata_profile = deepcopy(settings.REPORT_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

    def metadata_process(self):
        # Tasks
        tasks = self.get("tasks")
        if isinstance(tasks, list):
            for index, task in enumerate(tasks):
                if not isinstance(task, ReportTask):
                    task = ReportTask(task)
                    list.__setitem__(tasks, index, task)
            if not isinstance(tasks, helpers.ControlledList):
                tasks = helpers.ControlledList(tasks)
                tasks.__onchange__(self.metadata_process)
                dict.__setitem__(self, "tasks", tasks)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors


class ReportTask(Metadata):
    """Report task representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import ReportTask`

    Parameters:
        descriptor? (str|dict): schema descriptor
        time (float): validation time
        scope (str[]): validation scope
        partial (bool): wehter validation was partial
        errors (Error[]): validation errors
        task (Task): validation task

    # Raises
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        resource=None,
        time=None,
        scope=None,
        partial=None,
        errors=None,
    ):
        # Store provided
        self.setinitial("resource", resource)
        self.setinitial("time", time)
        self.setinitial("scope", scope)
        self.setinitial("partial", partial)
        self.setinitial("errors", errors)
        super().__init__(descriptor)

        # Store computed
        self.setinitial("stats", {"errors": len(self.errors)})
        self.setinitial("valid", not self.errors)

    @property
    def resource(self):
        """
        Returns:
            Resource: resource
        """
        return self["resource"]

    @property
    def time(self):
        """
        Returns:
            float: validation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self["valid"]

    @property
    def scope(self):
        """
        Returns:
            str[]: validation scope
        """
        return self["scope"]

    @property
    def partial(self):
        """
        Returns:
            bool: if validation partial
        """
        return self["partial"]

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self["stats"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self["errors"]

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

    # Expand

    def expand(self):
        """Expand metadata"""
        self.resource.expand()

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

    # Summary

    def to_summary(
        self,
    ) -> str:
        """Generate summary for validation task"

        Returns:
            str: validation summary
        """
        source = self.resource.path or self.resource.name
        if source and isinstance(source, list):
            source = ",".join(source)
        # For zipped resources append file name
        if self.resource.innerpath:
            source = f"{source} => {self.resource.innerpath}"
        # Prepare error lists and last row checked(in case of partial validation)
        error_list = {}
        for error in self.errors:
            error_title = f"{error.name} ({error.code})"
            if error_title not in error_list:
                error_list[error_title] = 0
            error_list[error_title] += 1
            if self.partial:
                last_row_checked = error.get("rowPosition", "")
        rows_checked = last_row_checked if self.partial else None
        unit = None
        file_size = self.resource.stats["bytes"]
        if file_size > 0:
            unit = helpers.format_bytes(file_size)
        not_found_text = ""
        if not unit:
            if not self.resource.innerpath:
                not_found_text = "(Not Found)"
        content = [
            [f"File name {not_found_text}", source],
            [f"File size { f'({unit})' if unit else '' }", file_size or "N/A"],
            ["Total Time Taken (sec)", self.time],
        ]
        if rows_checked:
            content.append(["Rows Checked(Partial)**", rows_checked])
        if error_list:
            content.append(["Total Errors", sum(error_list.values())])
        for code, count in error_list.items():
            content.append([code, count])
        return str(
            tabulate(content, headers=["Description", "Size/Name/Count"], tablefmt="grid")
        )

    # Metadata

    metadata_Error = ReportError
    metadata_profile = settings.REPORT_PROFILE["properties"]["tasks"]["items"]

    def metadata_process(self):
        Resource = import_module("frictionless.resource").Resource

        # Resource
        resource = self.get("resource")
        if not isinstance(resource, Resource):
            resource = Resource(resource)
            dict.__setitem__(self, "resource", resource)
