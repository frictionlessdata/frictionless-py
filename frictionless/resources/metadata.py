from __future__ import annotations
from typing import TYPE_CHECKING
from ..catalog import Catalog
from .json import JsonResource

if TYPE_CHECKING:
    from ..resource import Resource


class MetadataResource(JsonResource):
    pass


class CatalogResource(MetadataResource):
    datatype = "catalog"

    def read_catalog(self) -> Catalog:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Catalog.from_descriptor(descriptor, basepath=self.basepath)


class ResourceResource(MetadataResource):
    datatype = "resource"

    def read_resource(self) -> Resource:
        return self


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
