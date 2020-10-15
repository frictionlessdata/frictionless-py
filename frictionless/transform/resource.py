from functools import partial


def transform_resource(resource, *, steps):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
    """
    resource.infer(only_sample=True)
    target = resource
    for step in steps:
        source = target
        target = source.to_copy()
        target.data = partial(step.transform_resource, source, target)
        target.format = "inline"
    return target
