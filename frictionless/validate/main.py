from importlib import import_module
from ..report import Report
from ..system import system


# TODO: rename source_type -> type?
# TODO: handle source_type not found error
# TODO: support Resource/Package instances as an input source
@Report.from_validate
def validate(source, source_type=None, **options):
    """Validate resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate`

    Parameters:
        source (dict|str): a data source
        source_type (str): source type - inquiry, package, resource, schema or table
        **options (dict): options for the underlaying function

    Returns:
        Report: validation report
    """
    if not source_type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        if file.type in ["table", "schema", "resource", "package", "inquiry"]:
            source_type = file.type
    module = import_module("frictionless.validate")
    validate = getattr(module, "validate_%s" % source_type)
    return validate(source, **options)
