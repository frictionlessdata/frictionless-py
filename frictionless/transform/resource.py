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
        # TODO: resource should handle it
        target.format = "inline"
        if source.data is not target.data:
            target.data = data_wrapper(target.data, step=step)

    return target


# Internal


def data_wrapper(data, *, step):
    try:
        yield from data() if callable(data) else data
    except Exception as exception:
        if isinstance(exception, exceptions.FrictionlessException):
            if exception.error.code == "step-error":
                raise
        error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
        raise exceptions.FrictionlessException(error) from exception
