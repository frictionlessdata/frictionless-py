from .exception import FrictionlessException
from .errors import Error, StatusError
from .metadata import Metadata
from . import config


# TODO: add descriptor support
class Status(Metadata):
    """Status representation.

    Parameters:
        descriptor? (str|dict): schema descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, *, time, errors, tasks):
        stats_errors = len(errors) + sum(task["stats"]["errors"] for task in tasks)
        self.setinitial("version", config.VERSION)
        self.setinitial("time", time)
        self.setinitial("valid", not errors and all(task["valid"] for task in tasks))
        self.setinitial("stats", {"errors": stats_errors, "tasks": len(tasks)})
        self.setinitial("errors", errors)
        self.setinitial("tasks", tasks)

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
            ReportTable[]: validation tasks
        """
        return self["tasks"]

    @property
    def task(self):
        """
        Returns:
            ReportTable: validation task (if there is only one)

        Raises:
            FrictionlessException: if there are more that 1 task
        """
        if len(self.tasks) != 1:
            error = Error(note='The "report.task" is available for single task reports')
            raise FrictionlessException(error)
        return self.tasks[0]

    # Metadata

    metadata_strict = True
    metadata_Error = StatusError
    metadata_profile = config.STATUS_PROFILE


# TODO: add descriptor support
class StatusTask(Metadata):
    """ Status Task representation"""

    def __init__(self, *, errors, target, type):
        self.setinitial("valid", not errors)
        self.setinitial("errors", errors)
        self.setinitial("target", target)
        self.setinitial("type", type)
        self.setinitial("stats", {"errors": len(errors)})

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self["valid"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self["errors"]

    @property
    def target(self):
        """
        Returns:
            any: validation target
        """
        return self["target"]

    @property
    def type(self):
        """
        Returns:
            any: validation target
        """
        return self["type"]

    # Metadata

    metadata_strict = True
    metadata_Error = StatusError
    metadata_profile = config.STATUS_PROFILE["properties"]["tasks"]["items"]
