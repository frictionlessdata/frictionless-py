from importlib import import_module
from ..exception import FrictionlessException
from ..system import system
from .. import errors


def transform(source, type=None, **options):
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
    module = import_module("frictionless.transform")
    transform = getattr(module, "transform_%s" % type, None)
    if transform is None:
        note = f"Not supported transform type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    return transform(source, **options)
