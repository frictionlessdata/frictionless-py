from __future__ import annotations
import functools
from copy import deepcopy
from importlib import import_module
from typing import TYPE_CHECKING, Optional, List, Any
from ..metadata import Metadata
from ..errors import Error, ReportError
from ..exception import FrictionlessException
from .validate import validate
from .. import settings
from .. import helpers

if TYPE_CHECKING:
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
        descriptor: Optional[Any] = None,
        *,
        time: Optional[float] = None,
        errors: Optional[List[Error]] = None,
        warning: Optional[str] = None,
        tasks: Optional[List[ReportTask]] = None,
    ):

        # Store provided
        self.setinitial("version", settings.VERSION)
        self.setinitial("time", time)
        self.setinitial("errors", errors)
        self.setinitial("warning", warning)
        self.setinitial("tasks", tasks)
        super().__init__(descriptor)

        # TODO: remove after metadata rework
        self.setdefault("errors", [])
        self.setdefault("tasks", [])

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
    def warning(self):
        """
        Returns:
            Error[]: validation warning
        """
        return self["warning"]

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
    def from_resource(
        resource: Resource,
        *,
        time: float,
        scope: List[str] = [],
        errors: List[Error] = [],
        warning: Optional[str] = None,
    ):
        """Create a report from a task"""
        return Report(
            tasks=[
                ReportTask(
                    name=resource.name,  # type: ignore
                    path=resource.path,  # type: ignore
                    innerpath=resource.innerpath,  # type: ignore
                    memory=resource.memory,  # type: ignore
                    tabular=resource.tabular,  # type: ignore
                    stats=resource.stats,  # type: ignore
                    warning=warning,
                    errors=errors,
                    scope=scope,
                    time=time,
                )
            ],
            time=time,
        )

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
        return self["name"]

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
