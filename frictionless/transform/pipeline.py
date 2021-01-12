from ..pipeline import Pipeline
from ..system import system


def transform_pipeline(source, **options):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): a pipeline descriptor
        **options (dict): Pipeline constructor options

    Returns:
        any: the pipeline output
    """
    native = isinstance(source, Pipeline)
    pipeline = source if native else system.create_pipeline(source)
    return pipeline.run()
