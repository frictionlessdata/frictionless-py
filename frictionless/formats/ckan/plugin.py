from ...plugin import Plugin
from .control import CkanControl
from .parser import CkanParser
from .storage import CkanStorage


# Plugin


class CkanPlugin(Plugin):
    """Plugin for CKAN"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("code") == "ckan":
            return CkanControl.from_descriptor(descriptor)

    def create_parser(self, resource):
        if resource.format == "ckan":
            return CkanParser(resource)

    def create_storage(self, name, source, **options):
        if name == "ckan":
            return CkanStorage(source, **options)

    def detect_resource(self, resource):
        if resource.format == "ckan":
            resource.type = "table"
