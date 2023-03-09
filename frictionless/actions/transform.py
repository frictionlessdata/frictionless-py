from typing import Optional, List, Any, Union
from ..pipeline import Pipeline, Step
from ..resource import Resource


def transform(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Pipeline
    pipeline: Optional[Union[Pipeline, str]] = None,
    steps: Optional[List[Step]] = None,
    **options,
):
    """Transform resource

    Parameters:
        source: data source
        type: data type - package, resource or pipeline (default: infer)
        steps: transform steps
        **options: options for the underlaying constructor

    Returns:
        the transform result
    """

    # Create pipeline
    if isinstance(pipeline, str):
        pipeline = Pipeline.from_descriptor(pipeline)
    elif not pipeline:
        pipeline = Pipeline(steps=steps or [])

    # Transform resource
    resource = Resource(source, datatype=type or "", **options)
    return resource.transform(pipeline)
