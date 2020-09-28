import os
import glob
from pathlib import Path
from importlib import import_module
from ..package import Package
from .. import helpers


def extract(source, *, source_type=None, process=None, stream=False, **options):
    """Extract resource rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract`

    Parameters:
        source (dict|str): data source
        source_type (str): source type - package, resource or table
        process? (func): a row processor function
        stream? (bool): return a row stream(s) instead of loading into memory
        **options (dict): options for the underlaying function

    Returns:
        Row[]|{path: Row[]}: rows in a form depending on the source type
    """
    module = import_module("frictionless.extract")

    # Normalize source
    # NOTE: move to lower-levels
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    # NOTE: move to helpers
    if not source_type:
        if not callable(source):
            if isinstance(source, list) or glob.has_magic(source):
                package = Package()
                package.infer(source)
                source = package
            elif os.path.isdir(source):
                package = Package()
                package.infer(f"{source}/*")
                source = package
        source_type = helpers.detect_source_type(source)

    # Extract source
    extract = getattr(module, "extract_%s" % source_type)
    return extract(source, process=process, stream=stream, **options)
