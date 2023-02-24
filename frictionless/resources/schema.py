from ..resource import Resource


class JsonSchemaResource(Resource):
    type = "schema/json"


class TableSchemaResource(Resource):
    type = "schema/table"
