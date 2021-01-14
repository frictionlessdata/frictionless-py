import stringcase
from copy import deepcopy
from importlib import import_module
from .exception import FrictionlessException
from .errors import PipelineError, TaskError
from .status import Status, StatusTask
from .metadata import Metadata
from .resource import Resource
from .package import Package
from . import helpers
from . import config


# TODO: Add PipelineTask class?
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
        return self["tasks"]

    # Run

    # TODO: support parallel runner
    def run(self):
        """Run the pipeline"""
        tasks = []
        timer = helpers.Timer()
        for source in self.tasks:
            errors = []
            try:
                target = self.run_task(source)
            except Exception as exception:
                errors.append(TaskError(note=str(exception)))
            tasks.append(StatusTask(errors=errors, target=target, type=source["type"]))
        return Status(tasks=tasks, time=timer.time, errors=[])

    def run_task(self, task):
        """Run the pipeline task"""
        transsteps = import_module("frictionless.steps")
        transforms = import_module("frictionless.transform")

        # Prepare steps
        steps = []
        for step in task["steps"]:
            desc = deepcopy(step)
            # TODO: we need the same for nested steps like steps.resource_transform
            name = stringcase.snakecase(desc.pop("step", ""))
            func = getattr(transsteps, name, None)
            if func is None:
                note = f"Not supported step type: {name}"
                raise FrictionlessException(TaskError(note=note))
            steps.append(func(**helpers.create_options(desc)))

        # Resource transform
        if task["type"] == "resource":
            source = Resource(task.get("source"))
            return transforms.transform_resource(source, steps=steps)

        # Package transform
        elif task["type"] == "package":
            source = Package(task.get("source"))
            return transforms.transform_package(source, steps=steps)

        # Not supported transform
        type = task["type"]
        note = f'Transform type "{type}" is not supported'
        raise FrictionlessException(PipelineError(note=note))

    # Metadata

    metadata_strict = True
    metadata_Error = PipelineError
    metadata_profile = config.PIPELINE_PROFILE
