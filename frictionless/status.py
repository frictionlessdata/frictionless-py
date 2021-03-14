from copy import deepcopy
from .exception import FrictionlessException
from .errors import Error, StatusError
from .metadata import Metadata
from .resource import Resource
from .package import Package
from . import helpers
from . import config


class Status(Metadata):
    """Status representation.

    Parameters:
        descriptor? (str|dict): schema descriptor

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
            float: transformation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: transformation result
        """
        return self["valid"]

    @property
    def stats(self):
        """
        Returns:
            dict: transformation stats
        """
        return self["stats"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: transformation errors
        """
        return self["errors"]

    @property
    def tasks(self):
        """
        Returns:
            ReportTable[]: transformation tasks
        """
        return self["tasks"]

    @property
    def task(self):
        """
        Returns:
            ReportTable: transformation task (if there is only one)

        Raises:
            FrictionlessException: if there are more that 1 task
        """
        if len(self.tasks) != 1:
            error = Error(note='The "status.task" is available for single task reports')
            raise FrictionlessException(error)
        return self.tasks[0]

    # Metadata

    metadata_Error = StatusError
    metadata_profile = deepcopy(config.STATUS_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

    def metadata_process(self):

        # Tasks
        tasks = self.get("tasks")
        if isinstance(tasks, list):
            for index, task in enumerate(tasks):
                if not isinstance(task, StatusTask):
                    task = StatusTask(task)
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


class StatusTask(Metadata):
    """ Status Task representation"""

    def __init__(
        self,
        descriptor=None,
        *,
        time=None,
        errors=None,
        target=None,
        type=None,
    ):

        # Store provided
        self.setinitial("time", not errors)
        self.setinitial("errors", errors)
        self.setinitial("target", target)
        self.setinitial("type", type)
        super().__init__(descriptor)

        # Store computed
        self.setinitial("stats", {"errors": len(self.errors)})
        self.setinitial("valid", not self.errors)

    @property
    def time(self):
        """
        Returns:
            dict: transformation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: transformation result
        """
        return self["valid"]

    @property
    def stats(self):
        """
        Returns:
            dict: transformation stats
        """
        return self["stats"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: transformation errors
        """
        return self["errors"]

    @property
    def target(self):
        """
        Returns:
            any: transformation target
        """
        return self["target"]

    @property
    def type(self):
        """
        Returns:
            any: transformation target
        """
        return self["type"]

    # Metadata

    metadata_Error = StatusError
    metadata_profile = config.STATUS_PROFILE["properties"]["tasks"]["items"]

    def metadata_process(self):

        # Target
        target = self.get("target")
        if not isinstance(target, Metadata):
            target = Resource(target) if self.type == "resource" else Package(target)
            dict.__setitem__(self, "target", target)
