from __future__ import annotations
from typing import TYPE_CHECKING
from ...pipeline import Pipeline
from ...exception import FrictionlessException
from ...helpers import get_name
from ... import errors

if TYPE_CHECKING:
    from ..package import Package


def transform(self: Package, pipeline: Pipeline):
    for step in pipeline.steps:
        try:
            step.transform_package(self)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
    return self
