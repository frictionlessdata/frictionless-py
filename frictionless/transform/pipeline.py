from ..system import system


def transform_pipeline(source):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): a pipeline descriptor

    """

    # Run pipeline
    pipeline = system.create_pipeline(source)
    return pipeline.run()
