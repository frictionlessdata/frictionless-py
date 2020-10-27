from ..step import Step


# TODO: don't modify input
# TODO: implement error handling
def transform_resource(resource, *, steps):
    """Transform resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_resource`

    Parameters:
        source (any): data source
    """
    resource.infer(only_sample=True)
    target = resource.to_copy()
    # TODO: should be handled by Resource.to_copy
    target.basepath = resource.basepath
    for step in steps:
        source = target
        target = source.to_copy()
        # TODO: should be handled by Resource.to_copy
        target.basepath = source.basepath
        update = step.transform_resource if isinstance(step, Step) else step
        # TODO: review
        update(source, target)
        # TODO: resource should handle it
        target.format = "inline"
    return target
