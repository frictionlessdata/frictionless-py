from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ...pipeline import Pipeline
from ...exception import FrictionlessException
from ...helpers import get_name
from ... import errors

if TYPE_CHECKING:
    from ..resource import Resource


# TODO: save transform info into resource.stats?
def transform(self: Resource, pipeline: Optional[Pipeline] = None):
    """Transform resource

    Parameters:
        steps (Step[]): transform steps

    Returns:
        Resource: the transform result
    """

    # Prepare resource
    self.infer()

    # Prepare pipeline
    pipeline = pipeline or self.pipeline or Pipeline()

    # Run transforms
    for step in pipeline.steps:
        data = self.data

        # Transform
        try:
            step.transform_resource(self)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        # TODO: review this code
        # https://github.com/frictionlessdata/frictionless-py/issues/722
        if self.data is not data:
            self.path = None
            self.data = DataWithErrorHandling(self.data, step=step)
            self.scheme = ""
            self.format = "inline"
            self.encoding = None
            self.compression = None
            self.extrapaths = []
            self.innerpath = None
            self.dialect = None
            self.stats = None

    return self


# TODO: do we need error handling here?
class DataWithErrorHandling:
    def __init__(self, data, *, step):
        self.data = data
        self.step = step

    def __repr__(self):
        return "<transformed-data>"

    def __iter__(self):
        try:
            yield from self.data() if callable(self.data) else self.data
        except Exception as exception:
            if isinstance(exception, FrictionlessException):
                if exception.error.type == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
