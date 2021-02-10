from copy import deepcopy
from multiprocessing import Pool
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

        # Create state
        statuses = []
        timer = helpers.Timer()

        # Validate pipeline
        if self.metadata_errors:
            return Status(time=timer.time, errors=self.metadata_errors, tasks=[])

        # Transform sequentially
        if not parallel:
            for task in self.tasks:
                status = task.run()
                statuses.append(status)

        # Transform in-parallel
        else:
            with Pool() as pool:
                task_descriptors = [task.to_dict() for task in self.tasks]
                status_descriptors = pool.map(run_task_in_parallel, task_descriptors)
                for status_descriptor in status_descriptors:
                    statuses.append(Status(status_descriptor))

        # Return status
        tasks = []
        errors = []
        for status in statuses:
            tasks.extend(status["tasks"])
            errors.extend(status["errors"])
        return Status(time=timer.time, errors=[], tasks=tasks)

    # Metadata

    metadata_Error = PipelineError
    metadata_profile = deepcopy(config.PIPELINE_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

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

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors


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
        errors = []
        target = None
        timer = helpers.Timer()
        try:
            transform = import_module("frictionless").transform
            target = transform(self.source, type=self.type, steps=self.steps)
        except Exception as exception:
            errors.append(TaskError(note=str(exception)))
        task = StatusTask(time=timer.time, errors=errors, target=target, type=self.type)
        return Status(tasks=[task], time=timer.time, errors=[])

    # Metadata

    metadata_Error = PipelineError
    metadata_profile = config.PIPELINE_PROFILE["properties"]["tasks"]["items"]

    def metadata_process(self):

        # Source
        source = self.get("source")
        if not isinstance(source, Metadata):
            source = Resource(source) if self.type == "resource" else Package(source)
            dict.__setitem__(self, "source", source)


# Internal


def run_task_in_parallel(task_descriptor):
    task = PipelineTask(task_descriptor)
    status = task.run()
    status_descriptor = status.to_dict()
    return status_descriptor
