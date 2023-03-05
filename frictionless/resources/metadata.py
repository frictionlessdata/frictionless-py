from __future__ import annotations
from ..catalog import Catalog
from .json import JsonResource


class MetadataResource(JsonResource):
    pass


class CatalogResource(MetadataResource):
    datatype = "catalog"

    # Read

    def read_catalog(self) -> Catalog:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Catalog.from_descriptor(descriptor, basepath=self.basepath)


class DialectResource(MetadataResource):
    datatype = "dialect"


class JsonschemaResource(MetadataResource):
    datatype = "jsonschema"


class SchemaResource(MetadataResource):
    datatype = "schema"


class ChecklistResource(MetadataResource):
    datatype = "checklist"


class PipelineResource(MetadataResource):
    datatype = "pipeline"


class InquiryResource(MetadataResource):
    datatype = "inquiry"


class ReportResource(MetadataResource):
    datatype = "report"
