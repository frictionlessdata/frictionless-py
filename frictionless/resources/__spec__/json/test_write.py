from frictionless.resources import JsonResource

# General


def test_resource_write_json(tmpdir):
    source = JsonResource(path="data/table.json")
    target = source.write_json(path=str(tmpdir.join("table.json")))
    assert target.read_json() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]


def test_resource_write_json_yaml(tmpdir):
    source = JsonResource(path="data/table.yaml")
    target = source.write_json(path=str(tmpdir.join("table.yaml")))
    assert target.read_json() == [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"],
    ]
