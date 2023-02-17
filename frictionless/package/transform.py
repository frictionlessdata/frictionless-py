import types
from typing import TYPE_CHECKING
from ..step import Step
from ..system import system
from ..helpers import get_name
from ..exception import FrictionlessException
from .. import errors

if TYPE_CHECKING:
    from .package import Package


def transform(package: "Package", *, steps):
    """Transform package

    Parameters:
        source (any): data source
        steps (Step[]): transform steps
        **options (dict): Package constructor options

    Returns:
        Package: the transform result
    """

    # Prepare package
    package.infer()

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
            step.transform_package(package)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

    return package
