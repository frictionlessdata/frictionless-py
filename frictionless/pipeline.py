from importlib import import_module
from .errors import PipelineError, TaskError
from .status import Status, StatusTask
from .metadata import Metadata
from .resource import Resource
from .package import Package
from . import helpers
from . import config


class Pipeline(Metadata):
    """Pipeline representation.

    Parameters:
        descriptor? (str|dict): pipeline descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor, tasks=None):
        self.setinitial("tasks", tasks)
        super().__init__(descriptor)

    @property
    def tasks(self):
        """
        Returns:
            dict[]: tasks
        """
        tasks = self.get("tasks", [])
        return self.metadata_attach("tasks", tasks)

    # Run

    def run(self, *, parallel=False):
        """Run the pipeline"""
        tasks = []
        timer = helpers.Timer()
        for task in self.tasks:
            errors = []
            target = None
            task_timer = helpers.Timer()
            try:
                target = task.run()
            except Exception as exception:
                errors.append(TaskError(note=str(exception)))
            time = task_timer.time
            task = StatusTask(time=time, errors=errors, target=target, type=task.type)
            tasks.append(task)
        return Status(tasks=tasks, time=timer.time, errors=[])

    # Metadata

    metadata_strict = True
    metadata_Error = PipelineError
    metadata_profile = config.PIPELINE_PROFILE

    def metadata_process(self):

        # Tasks
        tasks = self.get("tasks")
        if isinstance(tasks, list):
            for index, task in enumerate(tasks):
                if not isinstance(task, PipelineTask):
                    task = PipelineTask(task)
                    list.__setitem__(tasks, index, task)
            if not isinstance(tasks, helpers.ControlledList):
                tasks = helpers.ControlledList(tasks)
                tasks.__onchange__(self.metadata_process)
                dict.__setitem__(self, "tasks", tasks)


class PipelineTask(Metadata):
    """Pipeline task representation.

    Parameters:
        descriptor? (str|dict): pipeline task descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, source=None, type=None, steps=None):
        self.setinitial("source", source)
        self.setinitial("type", type)
        self.setinitial("steps", steps)
        super().__init__(descriptor)

    @property
    def source(self):
        return self["source"]

    @property
    def type(self):
        return self["type"]

    @property
    def steps(self):
        return self["steps"]

    # Run

    def run(self):
        """Run the task"""
        transform = import_module("frictionless.transform").transform
        return transform(self.source, type=self.type, steps=self.steps)

    # Metadata

    metadata_strict = True
    metadata_Error = PipelineError
    metadata_profile = config.PIPELINE_PROFILE["properties"]["tasks"]["items"]

    def metadata_process(self):

        # Source
        source = self.get("source")
        if not isinstance(source, Metadata):
            source = Resource(source) if self.type == "resource" else Package(source)
            dict.__setitem__(self, "source", source)
