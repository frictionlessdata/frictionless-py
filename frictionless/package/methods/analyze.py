from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..package import Package


def analyze(self: Package, *, detailed=False):
    """Analyze the resources of the package

    This feature is currently experimental, and its API may change
    without warning.

    Parameters:
        detailed? (bool): detailed analysis

    Returns:
        dict: dict of resource analysis

    """
    result = {}
    for number, resource in enumerate(self.resources, start=1):
        key = resource.fullpath if not resource.memory else f"memory{number}"
        result[key] = resource.analyze(detailed=detailed)
    return result
