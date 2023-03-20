from frictionless.resources import JsonResource


# General


def test_resource_read_data():
    resource = JsonResource(path="data/table.json")
    assert resource.read_data() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]
