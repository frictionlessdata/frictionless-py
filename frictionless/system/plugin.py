from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type

if TYPE_CHECKING:
    from ..checklist import Check
    from ..dialect import Control
    from ..error import Error
    from ..package import Package
    from ..pipeline import Step
    from ..resource import Resource
    from ..schema import Field
    from .adapter import Adapter
    from .loader import Loader
    from .parser import Parser


class Plugin:
    """Plugin representation

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    # Hooks

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        """Create loader

        Parameters:
            resource (Resource): loader resource

        Returns:
            Loader: loader
        """
        pass

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ) -> Optional[Adapter]:
        """Create adapter

        Parameters:
            source: source
            control: control

        """
        pass

    def create_parser(self, resource: Resource) -> Optional[Parser]:
        """Create parser

        Parameters:
            resource (Resource): parser resource

        Returns:
            Parser: parser
        """
        pass

    def detect_resource(self, resource: Resource) -> None:
        """Hook into resource detection.

        Called on the final resource instance after the Detector has filled
        in path-derived fields (name, scheme, format, compression). Plugins
        guard themselves internally (e.g. `if resource.format == "csv"`) and
        fill in their own defaults (mediatype, scheme, seed data, ...).

        Parameters:
            resource (Resource): resource

        """
        pass

    def matches_datatype(self, resource: Resource) -> Optional[str]:
        """Return the datatype for a resource this plugin recognizes, or None.

        Must not mutate the resource. Used for class dispatch before the
        final Resource subclass is instantiated. First match wins across
        plugins; user-registered plugins have precedence over default plugins.

        Parameters:
            resource (Resource): resource to inspect

        Returns:
            Optional[str]: datatype name or None
        """
        pass

    def detect_field_candidates(self, candidates: List[dict[str, Any]]) -> None:
        """Detect field candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        pass

    def select_check_class(self, type: Optional[str] = None) -> Optional[Type[Check]]:
        pass

    def select_control_class(self, type: Optional[str] = None) -> Optional[Type[Control]]:
        pass

    def select_error_class(self, type: Optional[str] = None) -> Optional[Type[Error]]:
        pass

    def select_field_class(self, type: Optional[str] = None) -> Optional[Type[Field]]:
        pass

    def select_package_class(self, type: Optional[str] = None) -> Optional[Type[Package]]:
        pass

    def select_resource_class(
        self, type: Optional[str] = None, *, datatype: Optional[str] = None
    ) -> Optional[Type[Resource]]:
        pass

    def select_step_class(self, type: Optional[str] = None) -> Optional[Type[Step]]:
        pass
