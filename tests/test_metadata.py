from frictionless import Metadata


# General


def test_descriptor():
    metadata = Metadata({"key": "value"})
    assert metadata["key"] == "value"


def test_descriptor_from_path():
    metadata = Metadata("data/schema-valid.json")
    assert metadata["primaryKey"] == "id"


# Problems


def test_metadata_pprint_1029():
    metadata = Metadata("data/schema-valid.json")
    expected = """{'fields': [{'constraints': {'required': True},
             'description': 'The id.',
             'name': 'id',
             'title': 'ID',
             'type': 'integer'},
            {'constraints': {'required': True},
             'description': 'The name.',
             'name': 'name',
             'title': 'Name',
             'type': 'string'},
            {'constraints': {'required': True},
             'description': 'The age.',
             'name': 'age',
             'title': 'Age',
             'type': 'integer'}],
 'primaryKey': 'id'}"""
    assert repr(metadata) == expected
