from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any

if TYPE_CHECKING:
    from .file import File
    from .check import Check
    from .control import Control
    from .dialect import Dialect
    from .error import Error
    from .field import Field
    from .loader import Loader
    from .parser import Parser
    from .step import Step
    from .storage import Storage
    from .type import Type


# NOTE: implement create_resource so plugins can validate it (see #991)?


class Plugin:
    """Plugin representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Plugin`

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    code = "plugin"
    status = "stable"

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

    def create_control(self, file: File, *, descriptor: dict) -> Optional[Control]:
        """Create control

        Parameters:
            file (File): control file
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        pass

    def create_dialect(self, file: File, *, descriptor: dict) -> Optional[Dialect]:
        """Create dialect

        Parameters:
            file (File): dialect file
            descriptor (dict): dialect descriptor

        Returns:
            Dialect: dialect
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

    def create_field_candidates(self, candidates: List[dict]) -> Optional[List[dict]]:
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        pass

    def create_file(self, source: Any, **options) -> Optional[File]:
        """Create file

        Parameters:
            source (any): file source
            options (dict): file options

        Returns:
            File: file
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

    def create_parser(self, file: File) -> Optional[Parser]:
        """Create parser

        Parameters:
            file (File): parser file

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

    def create_type(self, field: Field) -> Optional[Type]:
        """Create type

        Parameters:
            field (Field): corresponding field

        Returns:
            Type: type
        """
        pass
