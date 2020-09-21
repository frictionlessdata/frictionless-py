from frictionless import Metadata


# General


def test_descriptor():
    metadata = Metadata({"key": "value"})
    assert metadata["key"] == "value"


def test_descriptor_from_path():
    metadata = Metadata("data/schema-valid.json")
    assert metadata["primaryKey"] == "id"
