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
    target = source.to_copy() if native else Resource(source, **options)
    target.infer()

    # Prepare steps
    for index, step in enumerate(steps):
        if not isinstance(step, Step):
            steps[index] = system.create_step(step)

    # Run transforms
    for step in steps:

        # Preprocess
        source = target
        target = source.to_copy()

        # Transform
        try:
            step.transform_resource(source, target)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if source.data is not target.data:
            target.data = DataWithErrorHandling(target.data, step=step)
            # TODO: can be removed when path/data updates is implemented for resource
            target.format = "inline"

    return target


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
