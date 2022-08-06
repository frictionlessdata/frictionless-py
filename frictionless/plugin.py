from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any, Type

if TYPE_CHECKING:
    from .resource import Resource, Loader, Parser
    from .package import Manager, Storage
    from .checklist import Check
    from .dialect import Control
    from .error import Error
    from .schema import Field
    from .pipeline import Step


class Plugin:
    """Plugin representation

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    # Hooks

    def create_check(self, descriptor: dict) -> Optional[Check]:
        """Create check

        Parameters:
            name (str): check name
            descriptor (dict): check descriptor

        Returns:
            Check: check
        """
        pass

    def create_control(self, descriptor: dict) -> Optional[Control]:
        """Create control

        Parameters:
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        pass

    def create_error(self, descriptor: dict) -> Optional[Error]:
        """Create error

        Parameters:
            descriptor (dict): error descriptor

        Returns:
            Error: error
        """
        pass

    def create_field(self, descriptor: dict) -> Optional[Field]:
        """Create field

        Parameters:
            descriptor (dict): field descriptor

        Returns:
            Field: field
        """
        pass

    def create_field_candidates(self, candidates: List[dict]) -> Optional[List[dict]]:
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        pass

    def create_loader(self, resource: Resource) -> Optional[Loader]:
        """Create loader

        Parameters:
            resource (Resource): loader resource

        Returns:
            Loader: loader
        """
        pass

    def create_manager(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
    ) -> Optional[Manager]:
        """Create manager

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

    def create_step(self, descriptor: dict) -> Optional[Step]:
        """Create step

        Parameters:
            descriptor (dict): step descriptor

        Returns:
            Step: step
        """
        pass

    def create_storage(self, name: str, source: Any, **options) -> Optional[Storage]:
        """Create storage

        Parameters:
            name (str): storage name
            options (str): storage options

        Returns:
            Storage: storage
        """
        pass

    def detect_resource(self, resource: Resource) -> None:
        """Hook into resource detection

        Parameters:
            resource (Resource): resource

        """
        pass

    def select_field_class(self, type: str) -> Optional[Type[Field]]:
        pass
