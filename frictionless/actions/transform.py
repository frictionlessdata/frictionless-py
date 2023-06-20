from typing import Any, List, Optional, Union

from ..exception import FrictionlessException
from ..package import Package
from ..pipeline import Pipeline, Step
from ..platform import platform
from ..resource import Resource


def transform(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Pipeline
    pipeline: Optional[Union[Pipeline, str]] = None,
    steps: Optional[List[Step]] = None,
    **options: Any,
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

    # Transform package
    if isinstance(source, Package):
        return source.transform(pipeline)

    # Create resource
    resource = (
        source
        if isinstance(source, Resource)
        else Resource(source, datatype=type, **options)
    )

    # Transform resource
    if not isinstance(resource, platform.frictionless_resources.Transformable):
        note = f'Resource with data type "{resource.datatype}" is not transformable'
        raise FrictionlessException(note)
    return resource.transform(pipeline)
