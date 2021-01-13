from importlib import import_module
from ..exception import FrictionlessException
from ..report import Report
from ..system import system
from .. import errors


@Report.from_validate
def validate(source, type=None, **options):
    """Validate resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate`

    Parameters:
        source (dict|str): a data source
        type (str): source type - inquiry, package, resource, schema or table
        **options (dict): options for the underlaying function

    Returns:
        Report: validation report
    """
    if not type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        if file.type in ["table", "schema", "resource", "package", "inquiry"]:
            type = "resource" if file.type == "table" else file.type
    module = import_module("frictionless.validate")
    validate = getattr(module, "validate_%s" % type, None)
    if validate is None:
        note = f"Not supported validate type: {type}"
        raise FrictionlessException(errors.Error(note=note))
    return validate(source, **options)
