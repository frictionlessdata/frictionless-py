from frictionless import Metadata, get_metadata_intersection

# General


def test_descriptor():
    metadata = Metadata({"key": "value"})
    assert metadata["key"] == "value"


def test_descriptor_from_path():
    metadata = Metadata("data/schema-valid.json")
    assert metadata["primaryKey"] == "id"


def test_get_metadata_intersection():

    metadata_one = Metadata(
        {
            "base_key": "base_value",
            "base_list": [1, 2],
            "base_changed_key": "thing1",
            "base_changed_list": [1, 2, 3, 4],
            "base_changed_list_of_dicts": [{1: 2}, {3: 4}],
            "nested_key": {"this_is_nested": 5},
            "nested_list": {"this_is_nested": [1, 2]},
            "nested_changed_key": {"thing1": 5},
            "nested_changed_list": {"this_is_nested": [1, 2, 3, 4]},
            "nested_changed_list_of_dicts": {
                "this_is_nested": [{1: 2}, {3: 4}],
                "this_is_also_nested": [{1: [{1: 1}, {2: 2}]}, {3: [4, 5]}],
            },
        }
    )
    metadata_two = Metadata(
        {
            "base_key": "base_value",
            "base_list": [1, 2],
            "base_changed_key": "thing2",
            "base_changed_list": [1, 2, 5, 6],
            "base_changed_list_of_dicts": [{1: 2}, {3: 4}, {5: 6}],
            "nested_key": {"this_is_nested": 5},
            "nested_list": {"this_is_nested": [1, 2]},
            "nested_changed_key": {"thing2": 5},
            "nested_changed_list": {"this_is_nested": [1, 2, 5, 6]},
            "nested_changed_list_of_dicts": {
                "this_is_nested": [{1: 2}, {3: 4}, {5: 6}],
                "this_is_also_nested": [{1: [{1: 1}, {2: 2}]}, {3: [4, 5, 6]}],
            },
        }
    )
    assert get_metadata_intersection(metadata_one, metadata_two) == {
        "base_key": "base_value",
        "base_list": [1, 2],
        "base_changed_list": [1, 2],
        "base_changed_list_of_dicts": [{1: 2}, {3: 4}],
        "nested_key": {"this_is_nested": 5},
        "nested_list": {"this_is_nested": [1, 2]},
        "nested_changed_key": {},
        "nested_changed_list": {"this_is_nested": [1, 2]},
        "nested_changed_list_of_dicts": {
            "this_is_nested": [{1: 2}, {3: 4}],
            "this_is_also_nested": [{1: [{1: 1}, {2: 2}]}],
        },
    }
