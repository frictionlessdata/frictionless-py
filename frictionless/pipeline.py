from importlib import import_module
from .exception import FrictionlessException
from .errors import PipelineError, TaskError
from .status import Status, StatusTask
from .metadata import Metadata
from .resource import Resource
from .package import Package
from . import helpers
from . import config


# TODO: move validation logic to validate_inquiry?
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

    # TODO: support parallel runner
    def run(self, *, parallel=False):
        """Run the pipeline"""
        tasks = []
        timer = helpers.Timer()
        for task in self.tasks:
            errors = []
            target = None
            try:
                target = task.run()
            except Exception as exception:
                errors.append(TaskError(note=str(exception)))
            tasks.append(StatusTask(errors=errors, target=target, type=task.type))
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


# TODO: should we metadata_process task.source -> Resource/Package?
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

    def run(self):
        """Run the task"""
        transforms = import_module("frictionless.transform")

        # Resource transform
        if self.type == "resource":
            source = Resource(self.source)
            return transforms.transform_resource(source, steps=self.steps)

        # Package transform
        elif self.type == "package":
            source = Package(self.source)
            return transforms.transform_package(source, steps=self.steps)

        # Not supported transform
        note = f'Transform type "{self.type}" is not supported'
        raise FrictionlessException(PipelineError(note=note))

    # Metadata

    metadata_strict = True
    metadata_Error = PipelineError
    metadata_profile = config.PIPELINE_PROFILE["properties"]["tasks"]["items"]
