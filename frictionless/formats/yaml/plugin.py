from __future__ import annotations
from typing import TYPE_CHECKING
from ...system import Plugin
from .control import YamlControl
from .parser import YamlParser

if TYPE_CHECKING:
    from ...resource import Resource


class YamlPlugin(Plugin):
    """Plugin for Yaml"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "yaml":
            return YamlParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format == "yaml":
            resource.mediatype = "text/yaml"

    def select_Control(self, type):
        if type == "yaml":
            return YamlControl
