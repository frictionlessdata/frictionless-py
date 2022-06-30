from frictionless import Resource
from frictionless.plugins.json import JsonControl


# General


def test_json_dialect():
    with Resource(path="data/table.json") as resource:
        assert isinstance(resource.dialect.get_control("json"), JsonControl)
