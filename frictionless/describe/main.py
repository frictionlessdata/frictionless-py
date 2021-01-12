from importlib import import_module
from ..exception import FrictionlessException
from ..system import system
from .. import errors


def describe(source, *, type=None, **options):
    """Describe the data source

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe`

    Parameters:
        source (any): data source
        type (str): source type - `schema`, `resource` or `package` (default: infer)
        **options (dict): options for the underlaying describe function

    Returns:
        Package|Resource|Schema: metadata
    """
    if not type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        type = "package" if file.multipart else "resource"
    module = import_module("frictionless.describe")
    describe = getattr(module, "describe_%s" % type, None)
    if describe is None:
        note = f"Not supported describe type: {type}"
        raise FrictionlessException(errors.Error(note=note))
    return describe(source, **options)
