from typing import Optional, List, Any
from ..step import Step
from ..system import system
from ..package import Package
from ..resource import Resource
from ..exception import FrictionlessException
from .. import errors


# TODO: here we'd like to accept both pipeline + individual options


def transform(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    steps: List[Step],
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

    # Transform object
    if type == "package":
        package = Package(source, **options)
        return package.transform(steps=steps)
    elif type == "resource":
        resource = Resource(source, **options)
        return resource.transform(steps=steps)

    # Not supported
    note = f"Not supported transform type: {type}"
    raise FrictionlessException(errors.GeneralError(note=note))
