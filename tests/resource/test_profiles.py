from frictionless import Resource


# General


def test_resource_profiles():
    profile = "data/resource.profile.json"
    resource = Resource(path="data/table.csv", profiles=[profile])
    assert resource.profiles == [profile]
    assert resource.metadata_errors[0].type == "resource-error"
    assert resource.metadata_errors[0].note == "'requiredProperty' is a required property"
    resource.profiles = []
    assert resource.metadata_valid


def test_resource_profiles_from_dict():
    profile = {"type": "object", "required": ["requiredProperty"]}
    resource = Resource(path="data/table.csv", profiles=[profile])
    assert resource.profiles == [profile]
    assert resource.metadata_errors[0].type == "resource-error"
    assert resource.metadata_errors[0].note == "'requiredProperty' is a required property"
    resource.profiles = []
    assert resource.metadata_valid
