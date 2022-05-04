from ...exception import FrictionlessException
from ...parser import Parser
from ... import errors
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
        storage = CkanStorage(self.resource.fullpath, dialect=self.resource.dialect)
        resource = storage.read_resource(self.resource.dialect.resource)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        storage = CkanStorage(target.fullpath, dialect=target.dialect)
        if not target.dialect.resource:
            note = 'Please provide "dialect.resource" for writing'
            raise FrictionlessException(errors.StorageError(note=note))
        source.name = target.dialect.resource
        storage.write_resource(source, force=True)
