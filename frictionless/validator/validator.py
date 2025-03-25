from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..package import Package
    from ..resource import Resource


class Validator:
    """
    Validator is deprecated, and only kept for backwards compatibility.

    There is no plan to remove this class in future versions.
    """

    def validate_package(self, package: Package, *args: Any, **kwargs: Any):
        """
        Validator.validate_package is deprecated, use and see Package.validate
        instead.

        There is no plan to remove this method in future versions.
        """
        package.validate(*args, **kwargs)

    # Resource

    def validate_resource(self, resource: Resource, *args: Any, **kwargs: Any):
        """
        Validator.validate_resource is deprecated, use and see Resource.validate
        instead.

        There is no plan to remove this method in future versions.
        """
        resource.validate(*args, **kwargs)
