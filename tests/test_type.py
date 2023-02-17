import pytest
from frictionless import system, Plugin, Type, Resource, Schema, Field, describe


# General


def test_type_custom(custom_plugin):
    schema = Schema(
        fields=[
            Field(name="integer", type="integer"),
            Field(name="custom", type="custom"),
        ]
    )
    with Resource(path="data/table.csv", schema=schema) as resource:
        assert resource.read_rows() == [
            {"integer": 1, "custom": ["english"]},
            {"integer": 2, "custom": ["中国人"]},
        ]


def test_type_custom_detect(custom_plugin):
    resource = describe("data/table.csv")
    assert resource.schema.fields[0].type == "custom"
    assert resource.schema.fields[1].type == "custom"


# Fixtures


@pytest.fixture
def custom_plugin():
    # Type
    class CustomType(Type):
        def read_cell(self, cell):
            return [cell]

    # Plugin
    class CustomPlugin(Plugin):
        def create_candidates(self, candidates):
            candidates.insert(0, {"type": "custom"})

        def create_type(self, field):
            if field.type == "custom":
                return CustomType(field)

    # System
    plugin = CustomPlugin()
    system.register("custom", plugin)
    yield plugin
    system.deregister("custom")
