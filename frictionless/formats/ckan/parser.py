# type: ignore
from ...exception import FrictionlessException
from .control import CkanControl
from ...resource import Parser
from .storage import CkanStorage


class CkanParser(Parser):
    """Ckan parser implementation."""

    supported_types = [
        "string",
    ]

    # Read

    def read_cell_stream_create(self):
        control = CkanControl.from_dialect(self.resource.dialect)
        storage = CkanStorage(self.resource.fullpath, control=control)
        resource = storage.read_resource(control.resource)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.cell_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, source):
        control = CkanControl.from_dialect(self.resource.dialect)
        storage = CkanStorage(self.resource.fullpath, control=control)
        if not control.resource:
            note = 'Please provide "dialect.resource" for writing'
            raise FrictionlessException(note)
        source.name = control.resource
        storage.write_resource(source, force=True)
