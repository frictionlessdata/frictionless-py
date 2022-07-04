from frictionless import Metadata


# General


def test_metadata():
    descriptor = Metadata.metadata_normalize({"key": "value"})
    assert descriptor["key"] == "value"


def test_metadata_from_path():
    descriptor = Metadata.metadata_normalize("data/schema-valid.json")
    assert descriptor["primaryKey"] == "id"
