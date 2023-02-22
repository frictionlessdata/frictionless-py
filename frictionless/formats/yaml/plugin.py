from __future__ import annotations
from ...records import PathDetails
from ...system import Plugin
from .control import YamlControl
from .parser import YamlParser


class YamlPlugin(Plugin):
    """Plugin for Yaml"""

    # Hooks

    def create_parser(self, resource):
        if resource.format == "yaml":
            return YamlParser(resource)

    def detect_path_details(self, details: PathDetails):
        if details.format == "yaml":
            details.mediatype = "text/yaml"

    def select_Control(self, type):
        if type == "yaml":
            return YamlControl
