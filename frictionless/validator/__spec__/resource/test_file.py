from frictionless import Resource

# General


def test_resource_validate_format_non_tabular():
    resource = Resource("data/table.bad")
    report = resource.validate()
    assert report.valid


def test_resource_validate_invalid_resource_standards_v2_strict():
    report = Resource.validate_descriptor({"path": "data/table.csv"})
    assert report.flatten(["type", "note"]) == [
        ["resource-error", "'name' is a required property"],
    ]
