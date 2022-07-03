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
    if not pipeline.metadata_valid:
        raise FrictionlessException(pipeline.metadata_errors[0])

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
        if self.data is not data:
            self.data = DataWithErrorHandling(self.data, step=step)  # type: ignore
            # NOTE:
            # We need rework self.data or move to self.__setattr__
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            self.scheme = ""  # type: ignore
            self.format = "inline"  # type: ignore
            dict.pop(self, "path", None)
            dict.pop(self, "hashing", None)
            dict.pop(self, "encoding", None)
            dict.pop(self, "innerpath", None)
            dict.pop(self, "compression", None)
            dict.pop(self, "control", None)
            dict.pop(self, "dialect", None)
            dict.pop(self, "layout", None)

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
                if exception.error.code == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
