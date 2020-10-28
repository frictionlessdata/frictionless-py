from ..step import Step
from ..helpers import get_name
from .. import exceptions
from .. import errors


def transform_resource(resource, *, steps):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
    """

    # Prepare
    target = resource.to_copy()
    target.infer(only_sample=True)

    # Run transforms
    for step in steps:

        # Preprocess
        source = target
        target = source.to_copy()

        # Transform
        try:
            transform = step.transform_resource if isinstance(step, Step) else step
            transform(source, target)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise exceptions.FrictionlessException(error) from exception

        # Postprocess
        if source.data is not target.data:
            target.data = DataWithErrorHandling(target.data, step=step)
            # NOTE: can be removed when path/data updates is implemented for resource
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
            if isinstance(exception, exceptions.FrictionlessException):
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise exceptions.FrictionlessException(error) from exception
