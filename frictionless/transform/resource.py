from ..step import Step


# TODO: implement error handling
def transform_resource(resource, *, steps):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
    """
    # TODO: don't modify input
    resource.infer(only_sample=True)
    target = resource.to_copy()
    # TODO: don't do this and provide "normalize" step?
    target.data = resource.read_rows
    # TODO: resource should handle it
    target.format = "inline"
    for step in steps:
        source = target
        target = source.to_copy()
        update = step.transform_resource if isinstance(step, Step) else step
        update(source, target)
        # TODO: resource should handle it
        target.format = "inline"
    return target
