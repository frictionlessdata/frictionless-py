from __future__ import annotations
from importlib import import_module


@staticmethod
def describe(source=None, *, stats=False, **options):
    """Describe the given source as a resource

    Parameters:
        source (any): data source
        stats? (bool): if `True` infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """
    Resource = import_module("frictionless").Resource
    resource = Resource(source, **options)
    resource.infer(stats=stats)
    return resource
