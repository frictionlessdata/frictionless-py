from frictionless import formats, resources

# General


def test_json_dialect():
    with resources.TableResource(path="data/table.json") as resource:
        assert isinstance(resource.dialect.get_control("json"), formats.JsonControl)
