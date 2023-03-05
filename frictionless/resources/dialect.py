from ..report import Report
from ..dialect import Dialect
from .metadata import MetadataResource


class DialectResource(MetadataResource):
    datatype = "dialect"

    # Read

    def read_dialect(self) -> Dialect:
        return Dialect.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Dialect.validate_descriptor(self.descriptor, basepath=self.basepath)
