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
        source = resource.to_copy()

        # Transform
        try:
            step.transform_resource(resource)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if resource.data is not source.data:
            resource.data = DataWithErrorHandling(source, data=resource.data, step=step)

    return resource


# Internal


class DataWithErrorHandling:
    def __init__(self, resource, *, data, step):
        self.resource = resource
        self.data = data
        self.step = step

    def __iter__(self):
        try:
            yield from self.data(self.resource) if callable(self.data) else self.data
        except Exception as exception:
            if isinstance(exception, FrictionlessException):
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
