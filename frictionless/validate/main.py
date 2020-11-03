import os
import glob
from pathlib import Path
from importlib import import_module
from ..package import Package
from ..report import Report
from .. import helpers


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
    module = import_module("frictionless.validate")

    # Normalize source
    # NOTE: move to lower-levels
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    # NOTE: move to helpers
    if not source_type:
        if source and isinstance(source, list) and isinstance(source[0], str):
            basepath = options.pop("basepath", None)
            trusted = options.pop("trusted", False)
            package = Package(basepath=basepath, trusted=trusted)
            package.infer(source)
            source = package
            source_type = "package"
        if isinstance(source, str):
            if glob.has_magic(source):
                package = Package()
                package.infer(source)
                source = package
                source_type = "package"
            elif os.path.isdir(source):
                package = Package()
                package.infer(f"{source}/*")
                source = package
                source_type = "package"
        if not source_type:
            source_type = helpers.detect_source_type(source)

    # Validate source
    validate = getattr(module, "validate_%s" % source_type)
    return validate(source, **options)
