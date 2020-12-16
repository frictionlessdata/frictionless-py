from frictionless import system, Plugin, Type, Resource, Schema, Field


def test_type_custom():

    # Type
    class CustomType(Type):
        def read_cell(self, cell):
            return [cell]

    # Plugin
    class CustomPlugin(Plugin):
        def create_type(self, field):
            if field.type == "custom":
                return CustomType(field)

    # Testing
    system.register("custom", CustomPlugin())
    schema = Schema(fields=[Field(type="integer"), Field(type="custom")])
    resource = Resource(path="data/table.csv", schema=schema)
    assert resource.read_rows() == [
        {"integer": 1, "custom": ["english"]},
        {"integer": 2, "custom": ["中国人"]},
    ]
