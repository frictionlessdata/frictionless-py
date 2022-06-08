import pytest
from frictionless import Schema


DESCRIPTOR_MIN = {"fields": [{"name": "id"}, {"name": "height", "type": "integer"}]}


# General


@pytest.mark.skip
def test_schema_descriptor_expand():
    schema = Schema(DESCRIPTOR_MIN)
    schema.expand()
    assert schema == {
        "fields": [
            {"name": "id", "type": "string", "format": "default"},
            {"name": "height", "type": "integer", "format": "default"},
        ],
        "missingValues": [""],
    }
