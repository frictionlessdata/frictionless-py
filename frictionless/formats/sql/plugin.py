from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlparse

from ...platform import platform
from ...system import Plugin
from . import settings
from .adapter import SqlAdapter
from .control import SqlControl
from .parser import SqlParser

if TYPE_CHECKING:
    from ...dialect import Control
    from ...resource import Resource


class SqlPlugin(Plugin):
    """Plugin for SQL"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if packagify:
            if isinstance(source, str):
                parsed = urlparse(source)
                for prefix in settings.SCHEME_PREFIXES:
                    if parsed.scheme.startswith(prefix):
                        engine = platform.sqlalchemy.create_engine(source)
                        return SqlAdapter(engine, control=control)  # type: ignore

    def create_parser(self, resource: Resource):
        if resource.format == "sql":
            return SqlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.scheme:
            for prefix in settings.SCHEME_PREFIXES:
                if resource.scheme.startswith(prefix):
                    resource.format = "sql"
                    resource.datatype = "table"
                    return

    def select_control_class(self, type: Optional[str] = None):
        if type == "sql":
            return SqlControl
