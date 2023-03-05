from __future__ import annotations
from typing import TYPE_CHECKING, Union
from ..catalog import Catalog
from .json import JsonResource

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


class MetadataResource(JsonResource):
    @property
    def descriptor(self) -> Union[IDescriptor, str]:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return descriptor


class CatalogResource(MetadataResource):
    datatype = "catalog"

    # Read

    def read_catalog(self) -> Catalog:
        return Catalog.from_descriptor(self.descriptor, basepath=self.basepath)


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
