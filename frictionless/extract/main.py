from importlib import import_module
from ..exception import FrictionlessException
from ..system import system
from .. import errors


def extract(source=None, *, type=None, process=None, stream=False, **options):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract`

    Parameters:
        source (dict|str): data source
        type (str): source type - package of resource (default: infer)
        process? (func): a row processor function
        stream? (bool): return a row stream(s) instead of loading into memory
        **options (dict): options for the underlaying function

    Returns:
        Row[]|{path: Row[]}: rows in a form depending on the source type
    """
    if not type:
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"
    module = import_module("frictionless.extract")
    extract = getattr(module, "extract_%s" % type, None)
    if extract is None:
        note = f"Not supported extract type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    return extract(source, process=process, stream=stream, **options)
