from typing import Optional, List, Any
from ..step import Step
from ..system import system
from ..package import Package
from ..resource import Resource
from ..pipeline import Pipeline
from ..exception import FrictionlessException
from .. import errors


# TODO: here we'd like to accept both pipeline + individual options


def transform(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Pipeline
    pipeline: Optional[Pipeline] = None,
    steps: Optional[List[Step]] = None,
    allow_parallel: Optional[bool] = False,
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
        pipeline = Pipeline(
            steps=steps,
            allow_parallel=allow_parallel,
        )

    # Transform source
    if type == "package":
        if not isinstance(source, Package):
            source = Package(source, **options)
        return source.transform(pipeline)
    elif type == "resource":
        if not isinstance(source, Resource):
            source = Resource(source, **options)
        return source.transform(pipeline)

    # Not supported
    note = f"Not supported transform type: {type}"
    raise FrictionlessException(errors.GeneralError(note=note))
