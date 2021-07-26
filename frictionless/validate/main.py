from importlib import import_module
from ..exception import FrictionlessException
from ..report import Report
from ..system import system
from .. import errors


@Report.from_validate
def validate(source=None, type=None, **options):
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
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"
    module = import_module("frictionless.validate")
    validate = getattr(module, "validate_%s" % type, None)
    if validate is None:
        note = f"Not supported validate type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    # NOTE:
    # Review whether it's a proper place for this (program sends a detector)
    # We might resolve it when we convert Detector to be a metadata
    if type in ["inquiry", "schema"]:
        options.pop("detector", None)
    return validate(source, **options)
