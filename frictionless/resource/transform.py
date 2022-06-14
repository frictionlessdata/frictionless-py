from typing import TYPE_CHECKING, Optional
from ..helpers import get_name
from ..pipeline import Pipeline
from ..exception import FrictionlessException
from .. import errors

if TYPE_CHECKING:
    from .resource import Resource


# TODO: save transform info into resource.stats?
def transform(resource: "Resource", pipeline: Optional[Pipeline] = None):
    """Transform resource

    Parameters:
        steps (Step[]): transform steps

    Returns:
        Resource: the transform result
    """

    # Prepare resource
    resource.infer()

    # Prepare pipeline
    pipeline = pipeline or resource.pipeline or Pipeline()
    if not pipeline.metadata_valid:
        raise FrictionlessException(pipeline.metadata_errors[0])

    # Run transforms
    for step in pipeline.steps:
        data = resource.data

        # Transform
        try:
            step.transform_resource(resource)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if resource.data is not data:
            resource.data = DataWithErrorHandling(resource.data, step=step)  # type: ignore
            # NOTE:
            # We need rework resource.data or move to resource.__setattr__
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            resource.scheme = ""  # type: ignore
            resource.format = "inline"  # type: ignore
            dict.pop(resource, "path", None)
            dict.pop(resource, "hashing", None)
            dict.pop(resource, "encoding", None)
            dict.pop(resource, "innerpath", None)
            dict.pop(resource, "compression", None)
            dict.pop(resource, "control", None)
            dict.pop(resource, "dialect", None)
            dict.pop(resource, "layout", None)

    return resource


# Internal


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
