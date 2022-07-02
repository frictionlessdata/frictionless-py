# type: ignore
from ...exception import FrictionlessException
from ...resource import Parser
from .storage import CkanStorage


class CkanParser(Parser):
    """Ckan parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanParser`
    """

    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        control = self.resource.dialect.get_control("ckan")
        storage = CkanStorage(self.resource.fullpath, control=control)
        resource = storage.read_resource(control.resource)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        control = target.dialect.get_control("ckan")
        storage = CkanStorage(target.fullpath, control=control)
        if not control.resource:
            note = 'Please provide "dialect.resource" for writing'
            raise FrictionlessException(note)
        source.name = control.resource
        storage.write_resource(source, force=True)
