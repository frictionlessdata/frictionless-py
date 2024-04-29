import pytest

from frictionless import FrictionlessException, Resource

# General


def test_resource_profiles_to_descriptor():
    profile = "data/resource.profile.json"
    resource = Resource(path="data/table.csv", profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        resource.to_descriptor(validate=True)
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == "'requiredProperty' is a required property"


def test_resource_profiles_from_descriptor():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource.from_descriptor(
            {
                "name": "name",
                "path": "data/table.csv",
                "profile": "data/profiles/required.json",
            }
        )
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note == "'requiredProperty' is a required property"


@pytest.mark.skip
@pytest.mark.parametrize("profile", ["data-resource", "tabular-data-resource"])
def test_resource_profile_type(profile):
    descriptor = {"name": "table", "path": "data/table.csv", "profile": profile}
    resource = Resource.from_descriptor(descriptor)
    descriptor = resource.to_descriptor()
    assert descriptor.get("profile") is None
