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
    results = {}
    for resource in self.resources:
        result = resource.analyze(detailed=detailed)
        locate = resource.name or resource.place
        results[locate] = result
    return results
