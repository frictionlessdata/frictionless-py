from ..step import Step
from ..package import Package
from ..helpers import get_name
from ..exception import FrictionlessException
from .. import errors


def transform_package(source, *, steps, **options):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): data source
        steps (Step[]): transform steps
        **options (dict): Package constructor options

    Returns:
        Package: the transform result
    """

    # Prepare
    native = isinstance(source, Package)
    target = source.to_copy() if native else Package(source, **options)
    target.infer()

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
            raise FrictionlessException(error) from exception

    return target
