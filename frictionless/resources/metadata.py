from ..resource import Resource


class MetadataResource(Resource):
    pass


class CatalogResource(Resource):
    type = "catalog"


class ResourceResource(Resource):
    type = "resource"


class DialectResource(Resource):
    type = "dialect"


class JsonSchemaResource(MetadataResource):
    type = "schema/json"


class TableSchemaResource(MetadataResource):
    type = "schema/table"


class ChecklistResource(MetadataResource):
    type = "checklist"


class PipelineResource(MetadataResource):
    type = "pipeline"


class InquiryResource(MetadataResource):
    type = "inquiry"


class ReportResource(MetadataResource):
    type = "report"
