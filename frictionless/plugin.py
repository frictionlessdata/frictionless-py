from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any

if TYPE_CHECKING:
    from .resource import Resource, Loader, Parser
    from .package import Storage
    from .checklist import Check
    from .dialect import Control
    from .error import Error
    from .schema import Field
    from .pipeline import Step


# NOTE: implement create_resource so plugins can validate it (see #991)?


class Plugin:
    """Plugin representation

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    code = "plugin"

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

    def create_loader(self, file: File) -> Optional[Loader]:
        """Create loader

        Parameters:
            file (File): loader file

        Returns:
            Loader: loader
        """
        pass

    def create_package(self, package: Resource) -> None:
        """Hook into package creation

        Parameters:
            package (Package): package

        """
        pass

    def create_parser(self, file: File) -> Optional[Parser]:
        """Create parser

        Parameters:
            file (File): parser file

        Returns:
            Parser: parser
        """
        pass

    def create_resource(self, resource: Resource) -> None:
        """Hook into resource creation

        Parameters:
            resource (Resource): resource

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
