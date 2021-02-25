import types
from ..step import Step
from ..system import system
from ..helpers import get_name
from ..resource import Resource
from ..exception import FrictionlessException
from .. import errors


def transform_resource(source, *, steps, **options):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
        steps (Step[]): transform steps
        **options (dict): Package constructor options

    Returns:
        Resource: the transform result
    """

    # Prepare resource
    native = isinstance(source, Resource)
    resource = source.to_copy() if native else Resource(source, **options)
    resource.infer()

    # Prepare steps
    for index, step in enumerate(steps):
        if not isinstance(step, Step):
            steps[index] = (
                Step(function=step)
                if isinstance(step, types.FunctionType)
                else system.create_step(step)
            )

    # Validate steps
    for step in steps:
        if step.metadata_errors:
            raise FrictionlessException(step.metadata_errors[0])

    # Run transforms
    for step in steps:

        # Transform
        try:
            temp = resource.to_copy()
            data = step.transform_resource(resource)
            if data:
                try:
                    next(data)
                except StopIteration:
                    pass
                data = DataWithErrorHandling(temp, step=step)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if data:
            resource = resource.to_copy()
            resource.data = data
            resource.scheme = ""
            resource.format = "inline"
            resource.pop("path", None)
            resource.pop("hashing", None)
            resource.pop("encoding", None)
            resource.pop("innerpath", None)
            resource.pop("compression", None)
            resource.pop("control", None)
            resource.pop("dialect", None)
            resource.pop("layout", None)

    return resource


# Internal


# NOTE:
# We might consider extending to the sample size
# Also, we can move here some inferring logic (see pivor/recast/transpose)


class DataWithErrorHandling:
    def __init__(self, resource, *, step):
        self.resource = resource
        self.step = step

    def __iter__(self):
        try:
            yield from self.step.transform_resource(self.resource.to_copy())
        except Exception as exception:
            if isinstance(exception, FrictionlessException):
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
