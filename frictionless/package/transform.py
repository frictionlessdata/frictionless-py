import types
from typing import TYPE_CHECKING, Optional, List
from ..step import Step
from ..system import system
from ..helpers import get_name
from ..pipeline import Pipeline
from ..exception import FrictionlessException
from .. import errors

if TYPE_CHECKING:
    from .package import Package


# TODO: save transform info into package.stats?
def transform(
    package: "Package",
    pipeline: Pipeline,
):
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

    # Prepare pipeline
    if not pipeline.metadata_valid:
        raise FrictionlessException(pipeline.metadata_errors[0])

    # Run transforms
    for step in pipeline.steps:

        # Transform
        try:
            step.transform_package(package)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

    return package
