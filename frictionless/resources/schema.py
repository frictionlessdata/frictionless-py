from ..report import Report
from ..schema import Schema
from .metadata import MetadataResource


class SchemaResource(MetadataResource):
    datatype = "schema"

    # Read

    def read_schema(self) -> Schema:
        return Schema.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Schema.validate_descriptor(self.descriptor, basepath=self.basepath)
