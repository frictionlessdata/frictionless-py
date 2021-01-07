from importlib import import_module
from ..system import system


# TODO: rename source_type -> type?
# TODO: handle source_type not found error
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
    if not source_type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        if file.type in ["table", "resource", "package"]:
            source_type = file.type
    module = import_module("frictionless.extract")
    extract = getattr(module, "extract_%s" % source_type)
    return extract(source, process=process, stream=stream, **options)
