from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import Pipeline


# TODO: have instead of `pipeline.run` (move its code here)?
def transform(pipeline: "Pipeline", *, parallel=False):
    """Transform package

    Parameters:
        **options (dict): Pipeline constructor options

    Returns:
        any: the pipeline output
    """
    return pipeline.run(parallel=parallel)
