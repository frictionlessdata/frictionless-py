from __future__ import annotations
from typing import TYPE_CHECKING
from ..pipeline import Pipeline
from ..exception import FrictionlessException
from ..dialect import Dialect
from ..helpers import get_name
from .. import errors

if TYPE_CHECKING:
    from ..package import Package
    from ..resources import TableResource


class Transformer:
    # Package

    def transform_package(self, package: Package, pipeline: Pipeline):
        for step in pipeline.steps:
            try:
                step.transform_package(package)
            except Exception as exception:
                error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
                raise FrictionlessException(error) from exception
        return package

    # Resource

    # TODO: save transform info into resource.stats?
    def transform_table_resource(self, resource: TableResource, pipeline: Pipeline):
        # Prepare resource
        resource.infer()

        # Prepare pipeline
        pipeline = pipeline or Pipeline()

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
            # TODO: review this code
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            if resource.data is not data:
                resource.path = None
                resource.data = DataWithErrorHandling(resource.data, step=step)
                resource.scheme = ""
                resource.format = "inline"
                resource.encoding = None
                resource.compression = None
                resource.extrapaths = []
                resource.innerpath = None
                resource.dialect = Dialect()
                resource.stats.md5 = None
                resource.stats.sha256 = None
                resource.stats.bytes = None
                resource.stats.fields = None
                resource.stats.rows = None

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
                if exception.error.type == "step-error":
                    raise
            error = errors.StepError(note=f'"{get_name(self.step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception
