from frictionless import Resource
from frictionless.plugins.json import JsonDialect


# General


def test_json_dialect():
    with Resource(path="data/table.json") as resource:
        assert isinstance(resource.dialect, JsonDialect)
