from ..step import Step
from ..helpers import get_name
from .. import exceptions
from .. import errors


# TODO: fix base path problems
# TODO: don't modify input
def transform_package(package, *, steps):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): data source
    """

    # Prepare
    package.infer(only_sample=True)
    target = package.to_copy()
    # TODO: should be handled by Package.to_copy
    target.basepath = package.basepath

    # Run transforms
    for step in steps:

        # Preprocess
        source = target
        target = source.to_copy()
        # TODO: should be handled by Package.to_copy
        target.basepath = source.basepath

        # Transform
        try:
            transform = step.transform_package if isinstance(step, Step) else step
            transform(source, target)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise exceptions.FrictionlessException(error) from exception

    return target
