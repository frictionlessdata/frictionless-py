from ..pipeline import Pipeline


def transform_pipeline(source):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): a pipeline descriptor

    """

    # Run pipeline
    pipeline = Pipeline(source)
    pipeline.run()
