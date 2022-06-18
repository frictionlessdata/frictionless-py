from typing import Optional, List, Any
from ..step import Step
from ..system import system
from ..package import Package
from ..resource import Resource
from ..pipeline import Pipeline
from ..exception import FrictionlessException


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

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform`

    Parameters:
        source (any): data source
        type (str): source type - package, resource or pipeline (default: infer)
        steps (Step[]): transform steps
        **options (dict): options for the underlaying constructor

    Returns:
        any: the transform result
    """

    # Infer type
    if not type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        type = "package" if file.multipart else "resource"

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
