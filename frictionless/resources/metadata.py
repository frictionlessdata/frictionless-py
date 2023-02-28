from .json import JsonResource


class MetadataResource(JsonResource):
    pass


class CatalogResource(MetadataResource):
    datatype = "catalog"


class ResourceResource(MetadataResource):
    datatype = "resource"


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
