import pytest
from frictionless import system, Plugin, Resource, Schema, Field, describe


# General


def test_type_custom(enable_custom_plugin):
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "integer", "type": "integer"},
                {"name": "custom", "type": "custom"},
            ]
        }
    )
    with Resource(path="data/table.csv", schema=schema) as resource:
        assert resource.read_rows() == [
            {"integer": 1, "custom": ["english"]},
            {"integer": 2, "custom": ["中国人"]},
        ]


def test_type_custom_detect(enable_custom_plugin):
    resource = describe("data/table.csv")
    assert isinstance(resource, Resource)
    assert resource.schema.fields[0].type == "custom"
    assert resource.schema.fields[1].type == "custom"


# Fixtures


@pytest.fixture
def enable_custom_plugin():

    # Field
    class CustomField(Field):
        type = "custom"

        def create_cell_reader(self):
            def cell_reader(cell):
                return [cell], None

            return cell_reader

    # Plugin
    class CustomPlugin(Plugin):
        def detect_field_candidates(self, candidates):
            candidates.insert(0, {"type": "custom"})

        def select_Field(self, type):
            if type == "custom":
                return CustomField

    # System
    plugin = CustomPlugin()
    system.register("custom", plugin)
    yield plugin
    system.deregister("custom")
