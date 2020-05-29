from goodtables import Descriptor


# General


def test_descriptor():
    descriptor = Descriptor(key='value')
    assert descriptor['key'] == 'value'


def test_descriptor_from_path():
    descriptor = Descriptor('data/schema.json')
    assert descriptor['primaryKey'] == 'id'
