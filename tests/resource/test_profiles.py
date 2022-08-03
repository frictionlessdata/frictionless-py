from frictionless import Resource


# General


def test_resource_profiles():
    profile = "data/resource.profile.json"
    resource = Resource(path="data/table.csv", profiles=[profile])
    error = resource.list_metadata_errors()[0]
    assert resource.profiles == [profile]
    assert error.type == "resource-error"
    assert error.note == "'requiredProperty' is a required property"
    resource.profiles = []
    assert resource.check_metadata_valid()


def test_resource_profiles_from_dict():
    profile = {"type": "object", "required": ["requiredProperty"]}
    resource = Resource(path="data/table.csv", profiles=[profile])
    error = resource.list_metadata_errors()[0]
    assert resource.profiles == [profile]
    assert error.type == "resource-error"
    assert error.note == "'requiredProperty' is a required property"
    resource.profiles = []
    assert resource.check_metadata_valid()
