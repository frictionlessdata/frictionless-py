from __future__ import annotations
from typing import TYPE_CHECKING
from urllib.parse import urlparse
from ...platform import platform
from ...system import Plugin
from .control import SqlControl
from .parser import SqlParser
from .adapter import SqlAdapter
from . import settings

if TYPE_CHECKING:
    from ...resource import Resource


class SqlPlugin(Plugin):
    """Plugin for SQL"""

    # Hooks

    def create_adapter(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            for prefix in settings.SCHEME_PREFIXES:
                if parsed.scheme.startswith(prefix):
                    engine = platform.sqlalchemy.create_engine(source)
                    return SqlAdapter(engine, control=control)  # type: ignore

    def create_parser(self, resource):
        if resource.format == "sql":
            return SqlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.scheme:
            for prefix in settings.SCHEME_PREFIXES:
                if resource.scheme.startswith(prefix):
                    resource.format = "sql"
                    resource.mediatype = "application/sql"
                    return

    def detect_resource_type(self, resource: Resource):
        if resource.format == "sql":
            return "table"

    def select_Control(self, type):
        if type == "sql":
            return SqlControl
