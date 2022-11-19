from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any, Type

if TYPE_CHECKING:
    from ..resource import Resource
    from ..checklist import Check
    from ..dialect import Control
    from ..error import Error
    from ..schema import Field
    from ..pipeline import Step
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

    def detect_field_candidates(self, candidates: List[dict]) -> Optional[List[dict]]:
        """Detect field candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        pass

    def detect_resource(self, resource: Resource) -> None:
        """Hook into resource detection

        Parameters:
            resource (Resource): resource

        """
        pass

    def select_Check(self, type: str) -> Optional[Type[Check]]:
        pass

    def select_Control(self, type: str) -> Optional[Type[Control]]:
        pass

    def select_Error(self, type: str) -> Optional[Type[Error]]:
        pass

    def select_Field(self, type: str) -> Optional[Type[Field]]:
        pass

    def select_Step(self, type: str) -> Optional[Type[Step]]:
        pass
