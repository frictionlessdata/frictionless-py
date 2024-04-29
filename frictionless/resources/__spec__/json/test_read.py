from frictionless.resources import JsonResource

# General


def test_resource_read_json():
    resource = JsonResource(path="data/table.json")
    assert resource.read_json() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_read_json_yaml():
    resource = JsonResource(path="data/table.yaml")
    assert resource.read_json() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]
