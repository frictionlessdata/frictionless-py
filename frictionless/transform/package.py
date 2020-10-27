from ..step import Step


# TODO: don't modify input
# TODO: implement error handling
def transform_package(package, *, steps):
    """Transform package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import transform_package`

    Parameters:
        source (any): data source
    """
    package.infer(only_sample=True)
    target = package.to_copy()
    for step in steps:
        source = target
        target = source.to_copy()
        update = step.transform_package if isinstance(step, Step) else step
        update(source, target)
    return target
