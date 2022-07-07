from typing import Optional, List, Any
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
    pipeline: Optional[Pipeline] = None,
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
        type = Detector.detect_descriptor(source)
        if not type:
            type = "resource"
            if helpers.is_expandable_source(source):
                type = "package"

    # Create pipeline
    if not pipeline:
        pipeline = Pipeline(steps=steps or [])

    # Transform package
    if type == "package":
        package = source
        if not isinstance(package, Package):
            package = Package(package, **options)
        return package.transform(pipeline)

    # Transform resource
    elif type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource(resource, **options)
        return resource.transform(pipeline)

    # Not supported
    raise FrictionlessException(f"Not supported transform type: {type}")
