import functools
from copy import deepcopy
from .resource import Resource
from .metadata import Metadata
from .errors import Error, TaskError, ReportError
from .exception import FrictionlessException
from . import helpers
from . import config


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

    def __init__(self, descriptor=None, *, time=None, errors=None, tasks=None):

        # Store provided
        self.setinitial("version", config.VERSION)
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

    # Metadata

    metadata_Error = ReportError
    metadata_profile = deepcopy(config.REPORT_PROFILE)
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
        errors=None
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

    # Metadata

    metadata_Error = ReportError
    metadata_profile = config.REPORT_PROFILE["properties"]["tasks"]["items"]

    def metadata_process(self):

        # Resource
        resource = self.get("resource")
        if not isinstance(resource, Resource):
            resource = Resource(resource)
            dict.__setitem__(self, "resource", resource)
