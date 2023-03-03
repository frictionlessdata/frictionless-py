from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ..resource import Resource
from ..catalog import Catalog
from .json import JsonResource

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction, IExtractedRows


class MetadataResource(JsonResource):
    pass


class CatalogResource(MetadataResource):
    datatype = "catalog"

    # Read

    def read_catalog(self) -> Catalog:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Catalog.from_descriptor(descriptor, basepath=self.basepath)


class ResourceResource(MetadataResource):
    datatype = "resource"

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> IExtractedRows:
        resource = self.read_resource()
        return resource.extract(
            name=name, filter=filter, process=process, limit_rows=limit_rows
        )

    # Read

    def read_resource(self) -> Resource:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return Resource.from_descriptor(descriptor, basepath=self.basepath)


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
