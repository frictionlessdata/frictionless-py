import pytest
from frictionless import system, Plugin, Resource, Schema, Field, describe


# General


@pytest.mark.xfail(reason="Custom field types are not yet supported")
def test_type_custom(custom_plugin):
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


@pytest.mark.xfail(reason="Custom field types are not yet supported")
def test_type_custom_detect(custom_plugin):
    resource = describe("data/table.csv")
    assert resource.schema.fields[0].type == "custom"
    assert resource.schema.fields[1].type == "custom"


# Fixtures


@pytest.fixture
def custom_plugin():

    # Field
    class CustomField(Field):
        def create_cell_reader(self):
            def cell_reader(cell):
                return [cell], None

            return cell_reader

    # Plugin
    class CustomPlugin(Plugin):
        def create_field(self, descriptor):
            if descriptor.get("type") == "custom":
                return CustomField.from_descriptor(descriptor)

        def create_field_candidates(self, candidates):
            candidates.insert(0, {"type": "custom"})

    # System
    plugin = CustomPlugin()
    system.register("custom", plugin)
    yield plugin
    system.deregister("custom")
