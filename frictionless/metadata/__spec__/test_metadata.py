import pytest

from frictionless import Metadata, Package, Resource, Schema, settings

# General


def test_metadata():
    descriptor = Metadata.metadata_retrieve({"key": "value"})
    assert descriptor["key"] == "value"


def test_metadata_from_path():
    descriptor = Metadata.metadata_retrieve("data/schema-valid.json")
    assert descriptor["primaryKey"] == "id"


# Data package version inference from `$schema` prop

# @pytest.mark.parametrize(
#     "Entity, descriptor",
#     (
#         (Package, {"resources": []}),
#         (Schema, {"fields": []}),
#         (Resource, {"name": "table", "path": "table.csv"}),
#     ),
#     ids=["package", "schema", "resource"],
# )
# @pytest.mark.parametrize(
#     "schema, expected",
#     (
#         # Absent `$schema`: the spec mandates v1 as the default
#         (None, "v1"),
#         # Standard datapackage.org profiles: the version is read from the URL
#         ("https://datapackage.org/profiles/1.0/datapackage.json", "v1"),
#         ("https://datapackage.org/profiles/2.0/schema.json", "v2"),
#         ("https://datapackage.org/profiles/2.1/dataresource.json", "v2"),
#         # Custom profile: fall back to the default constant
#         (
#             "https://example.com/my-profile.json",
#             settings.DEFAULT_CUSTOM_PROFILE_DATAPACKAGE_VERSION,
#         ),
#     ),
# )
# def test_datapackage_version_inferred_from_schema(Entity, descriptor, schema, expected):
#     # Test only for direct inference from the class `$schema` property,
#     # not inheritance
#     descriptor = dict(descriptor)
#     if schema is not None:
#         descriptor["$schema"] = schema
#     metadata = Entity.from_descriptor(descriptor)
#     assert metadata.datapackage_version == expected


# `$schema` (de)serialization

SCHEMA_PROFILE = "https://datapackage.org/profiles/2.0/datapackage.json"


@pytest.mark.parametrize(
    "Entity, descriptor",
    (
        (Package, {"resources": []}),
        (Schema, {"fields": []}),
        (Resource, {"name": "table", "path": "table.csv"}),
    ),
    ids=["package", "schema", "resource"],
)
def test_schema_profile_imported_from_descriptor(Entity, descriptor):
    metadata = Entity.from_descriptor({**descriptor, "$schema": SCHEMA_PROFILE})
    assert metadata._schema_profile == SCHEMA_PROFILE
    # `$schema` is consumed, not left over in `custom`
    assert "$schema" not in metadata.custom


@pytest.mark.parametrize(
    "Entity, kwargs",
    (
        (Package, {"resources": []}),
        (Schema, {"fields": []}),
        (Resource, {"name": "table", "path": "table.csv"}),
    ),
    ids=["package", "schema", "resource"],
)
def test_schema_profile_exported_to_descriptor(Entity, kwargs):
    metadata = Entity(schema_profile=SCHEMA_PROFILE, **kwargs)
    assert metadata.to_descriptor()["$schema"] == SCHEMA_PROFILE
