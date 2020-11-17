import os
import glob
from pathlib import Path
from importlib import import_module


# TODO: support only_sample
def describe(source, *, source_type=None, **options):
    """Describe the data source

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe`

    Parameters:
        source (any): data source
        source_type (str): source type - `schema`, `resource` or `package`
        **options (dict): options for the underlaying describe function

    Returns:
        Package|Resource|Schema: metadata
    """
    module = import_module("frictionless.describe")

    # Normalize source
    # NOTE: move to lower-levels
    if isinstance(source, Path):
        source = str(source)

    # Detect source type
    # NOTE: move to helpers
    if not source_type:
        source_type = "resource"
        if isinstance(source, list):
            if source and isinstance(source[0], str):
                source_type = "package"
        elif hasattr(source, "read"):
            source_type = "resource"
        elif glob.has_magic(source):
            source_type = "package"
        elif os.path.isdir(source):
            source_type = "package"

    # Describe source
    describe = getattr(module, "describe_%s" % source_type)
    return describe(source, **options)
