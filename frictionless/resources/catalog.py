from ..report import Report
from ..catalog import Catalog
from .metadata import MetadataResource


class CatalogResource(MetadataResource):
    datatype = "catalog"

    # Read

    def read_catalog(self) -> Catalog:
        return Catalog.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Catalog.validate_descriptor(self.descriptor, basepath=self.basepath)
