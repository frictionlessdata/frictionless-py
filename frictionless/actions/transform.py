from typing import Optional, List, Any, Union
from ..exception import FrictionlessException
from ..pipeline import Pipeline, Step
from ..resource import Resource
from ..detector import Detector
from ..package import Package
from .. import helpers


# TODO: here we'd like to accept both pipeline + individual options


def transform(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Pipeline
    pipeline: Optional[Union[Pipeline, str]] = None,
    steps: Optional[List[Step]] = None,
    **options,
):
    """Transform resource

    Parameters:
        source (any): data source
        type (str): source type - package, resource or pipeline (default: infer)
        steps (Step[]): transform steps
        **options (dict): options for the underlaying constructor

    Returns:
        any: the transform result
    """

    # Detect type
    if not type:
        type = getattr(source, "metadata_type", None)
    if not type:
        type = Detector.detect_descriptor(source)
    if not type:
        type = "resource"
        if helpers.is_expandable_source(source):
            type = "package"

    # Create pipeline
    if isinstance(pipeline, str):
        pipeline = Pipeline.from_descriptor(pipeline)
    elif not pipeline:
        pipeline = Pipeline(steps=steps or [])

    # Transform resource
    if type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource.from_options(source, **options)
        return resource.transform(pipeline)

    # Transform package
    if type == "package":
        # TODO: remove when we add these to names kwargs
        options.pop("schema", None)
        options.pop("dialect", None)
        options.pop("checklist", None)
        options.pop("pipeline", None)
        options.pop("stats", None)
        package = source
        if not isinstance(package, Package):
            package = Package.from_options(source, **options)
        return package.transform(pipeline)

    # Not supported
    raise FrictionlessException(f"Not supported transform type: {type}")
