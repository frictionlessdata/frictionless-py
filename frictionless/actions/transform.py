import types
import warnings
from ..step import Step
from ..system import system
from ..package import Package
from ..resource import Resource
from ..helpers import get_name
from ..exception import FrictionlessException
from ..pipeline import Pipeline
from .. import errors


def transform(source=None, type=None, **options):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform`

    Parameters:
        source (any): data source
        type (str): source type - package, resource or pipeline (default: infer)
        **options (dict): options for the underlaying function

    Returns:
        any: the transform result
    """
    if not type:
        type = "pipeline"
        if options:
            file = system.create_file(source, basepath=options.get("basepath", ""))
            if file.type in ["table", "resource"]:
                type = "resource"
            elif file.type == "package":
                type = "package"
    transform = globals().get("transform_%s" % type, None)
    if transform is None:
        note = f"Not supported transform type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    return transform(source, deprecate=False, **options)


def transform_package(source=None, *, steps, deprecate=True, **options):
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
    if deprecate:
        message = 'Function "transform" is deprecated (use "Package.transform").'
        warnings.warn(message, UserWarning)

    # Prepare package
    native = isinstance(source, Package)
    package = source.to_copy() if native else Package(source, **options)
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


def transform_pipeline(source=None, *, parallel=False, deprecate=True, **options):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): a pipeline descriptor
        **options (dict): Pipeline constructor options

    Returns:
        any: the pipeline output
    """
    if deprecate:
        message = (
            'Function "transform_pipeline" is deprecated (use "Pipeline.transform").'
        )
        warnings.warn(message, UserWarning)
    native = isinstance(source, Pipeline)
    pipeline = source if native else Pipeline(source)
    return pipeline.run(parallel=parallel)


def transform_resource(source=None, *, steps, deprecate=True, **options):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
        steps (Step[]): transform steps
        **options (dict): Package constructor options

    Returns:
        Resource: the transform result
    """
    if deprecate:
        message = (
            'Function "transform_resource" is deprecated (use "Resource.transform").'
        )
        warnings.warn(message, UserWarning)

    # Prepare resource
    native = isinstance(source, Resource)
    resource = source.to_copy() if native else Resource(source, **options)
    resource.infer()

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
        data = resource.data

        # Transform
        try:
            step.transform_resource(resource)
        except Exception as exception:
            error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
            raise FrictionlessException(error) from exception

        # Postprocess
        if resource.data is not data:
            resource.data = DataWithErrorHandling(resource.data, step=step)
            # NOTE:
            # We need rework resource.data or move to resource.__setattr__
            # https://github.com/frictionlessdata/frictionless-py/issues/722
            resource.scheme = ""
            resource.format = "inline"
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
