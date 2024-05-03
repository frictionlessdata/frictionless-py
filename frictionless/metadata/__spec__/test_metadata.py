from frictionless import Metadata

# General


def test_metadata():
    descriptor = Metadata.metadata_retrieve({"key": "value"})
    assert descriptor["key"] == "value"


def test_metadata_from_path():
    descriptor = Metadata.metadata_retrieve("data/schema-valid.json")
    assert descriptor["primaryKey"] == "id"
