import types
from ..step import Step
from ..system import system
from ..helpers import get_name
from ..resource import Resource
from ..exception import FrictionlessException
from .. import errors


def transform_resource(source=None, *, steps, **options):
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
        data = resource.data

        # Transform
        try:
            step.transform_resource(resource)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if resource.data is not data:
            resource.data = DataWithErrorHandling(resource.data, step=step)
            # NOTE:
            # We need rework resource.data or move to resource.__setattr__
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            resource.scheme = ""
            resource.format = "inline"
            dict.pop(resource, "path", None)
            dict.pop(resource, "hashing", None)
            dict.pop(resource, "encoding", None)
            dict.pop(resource, "innerpath", None)
            dict.pop(resource, "compression", None)
            dict.pop(resource, "control", None)
            dict.pop(resource, "dialect", None)
            dict.pop(resource, "layout", None)

    return resource


# Internal


class DataWithErrorHandling:
    def __init__(self, data, *, step):
        self.data = data
        self.step = step

    def __iter__(self):
        try:
            yield from self.data() if callable(self.data) else self.data
        except Exception as exception:
            if isinstance(exception, FrictionlessException):
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
