from ...plugin import Plugin
from .dialect import CkanDialect
from .parser import CkanParser
from .storage import CkanStorage


# Plugin


class CkanPlugin(Plugin):
    """Plugin for CKAN

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanPlugin`
    """

    code = "ckan"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "ckan":
            return CkanDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "ckan":
            return CkanParser(resource)

    def create_storage(self, name, source, **options):
        if name == "ckan":
            return CkanStorage(source, **options)
