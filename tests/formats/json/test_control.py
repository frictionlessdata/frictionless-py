from frictionless import Resource, formats


# General


def test_json_dialect():
    with Resource(path="data/table.json", type="table") as resource:
        assert isinstance(resource.dialect.get_control("json"), formats.JsonControl)
