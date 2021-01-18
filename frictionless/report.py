import functools
from copy import deepcopy
from .metadata import Metadata
from .errors import Error, TaskError, ReportError
from .exception import FrictionlessException
from . import config
from . import helpers


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

    # TODO: allow kwargs to be None
    def __init__(self, descriptor=None, *, time, errors, tasks):
        error_count = len(errors) + sum(tab["stats"]["errors"] for tab in tasks)
        self.setinitial("version", config.VERSION)
        self.setinitial("time", time)
        self.setinitial("valid", not errors and all(task["valid"] for task in tasks))
        self.setinitial("stats", {"errors": error_count, "tasks": len(tasks)})
        self.setinitial("errors", errors)
        self.setinitial("tasks", tasks)
        super().__init__(descriptor)

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

    def flatten(self, spec):
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

    # TODO: review
    #  metadata_strict = True
    metadata_Error = ReportError
    metadata_profile = deepcopy(config.REPORT_PROFILE)
    metadata_profile["properties"]["tasks"] = {
        "type": "array",
        "items": {"type": "object"},
    }

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

    # TODO: allow kwargs to be None
    def __init__(self, descriptor=None, *, resource, time, scope, partial, errors):
        self.setinitial("resource", resource)
        self.setinitial("time", time)
        self.setinitial("valid", not errors)
        self.setinitial("scope", scope)
        self.setinitial("partial", partial)
        self.setinitial("stats", {"errors": len(errors)})
        self.setinitial("errors", errors)
        super().__init__(descriptor)

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

    def flatten(self, spec):
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

    # TODO: review
    #  metadata_strict = True
    metadata_Error = ReportError
    metadata_profile = config.REPORT_PROFILE["properties"]["tasks"]["items"]
    # TODO: review: should we validate errors for performance reasons
    #  del metadata_profile["properties"]["errors"]
