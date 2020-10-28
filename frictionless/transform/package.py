from ..step import Step
from ..helpers import get_name
from .. import exceptions
from .. import errors


def transform_package(package, *, steps):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): data source
    """

    # Prepare
    target = package.to_copy()
    target.infer(only_sample=True)

    # Run transforms
    for step in steps:

        # Preprocess
        source = target
        target = source.to_copy()

        # Transform
        try:
            transform = step.transform_package if isinstance(step, Step) else step
            transform(source, target)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise exceptions.FrictionlessException(error) from exception

    return target
