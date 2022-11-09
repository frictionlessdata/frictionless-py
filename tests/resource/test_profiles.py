import pytest
from frictionless import Resource, FrictionlessException


# General


def test_resource_profiles_to_descriptor():
    profile = "data/resource.profile.json"
    resource = Resource(path="data/table.csv", profiles=[profile])
    with pytest.raises(FrictionlessException) as excinfo:
        resource.to_descriptor()
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == "'requiredProperty' is a required property"


def test_resource_profiles_from_descriptor():
    profile = {"type": "object", "required": ["requiredProperty"]}
    with pytest.raises(FrictionlessException) as excinfo:
        Resource.from_descriptor({"path": "data/table.csv", "profiles": [profile]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == "'requiredProperty' is a required property"


@pytest.mark.parametrize("profile", ["data-resource", "tabular-data-resource"])
def test_resource_profile_type(profile):
    resource = Resource(name="table", path="data/table.csv", profiles=[profile])
    descriptor = resource.to_descriptor()
    assert descriptor["profiles"] == [profile]
