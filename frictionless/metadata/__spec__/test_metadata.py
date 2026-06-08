import pytest

from frictionless import Metadata, Package, Resource, Schema, settings

# General


def test_metadata():
    descriptor = Metadata.metadata_retrieve({"key": "value"})
    assert descriptor["key"] == "value"


def test_metadata_from_path():
    descriptor = Metadata.metadata_retrieve("data/schema-valid.json")
    assert descriptor["primaryKey"] == "id"


<<<<<<< HEAD
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


=======
>>>>>>> cc5edd81 (🔴 Infer datapackage version from $schema prop)
@pytest.mark.parametrize(
    "Entity, descriptor",
    (
        (Package, {"resources": []}),
        (Schema, {"fields": []}),
        (Resource, {"name": "table", "path": "table.csv"}),
    ),
    ids=["package", "schema", "resource"],
)
<<<<<<< HEAD
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
=======
@pytest.mark.parametrize(
    "schema, expected",
    (
        # Absent `$schema`: the spec mandates v1 as the default
        (None, "v1"),
        # Standard datapackage.org profiles: the version is read from the URL
        ("https://datapackage.org/profiles/1.0/datapackage.json", "v1"),
        ("https://datapackage.org/profiles/2.0/schema.json", "v2"),
        ("https://datapackage.org/profiles/2.1/dataresource.json", "v2"),
        # Custom profile: fall back to the default constant
        (
            "https://example.com/my-profile.json",
            settings.DEFAULT_CUSTOM_PROFILE_DATAPACKAGE_VERSION,
        ),
    ),
)
def test_standard_version_inferred_from_schema(Entity, descriptor, schema, expected):
    # Test only for direct inference from the class `$schema` property,
    # not inheritance
    descriptor = dict(descriptor)
    if schema is not None:
        descriptor["$schema"] = schema
    metadata = Entity.from_descriptor(descriptor)
    assert metadata.standard_version == expected


# Inheritance from a parent entity
#
# When an entity is built as part of a parent (a resource inside a package),
# the parent's resolved version always takes precedence over what the child
# would infer on its own.

V1 = "https://datapackage.org/profiles/1.0/datapackage.json"
V2 = "https://datapackage.org/profiles/2.0/datapackage.json"


@pytest.mark.parametrize(
    "package_schema, resource_schema, expected",
    (
        # The parent wins, even with a misalignment, in whichever direction it goes
        (V2, V1, "v2"),
        (V1, V2, "v1"),
        # A package without `$schema` resolves to v1 and imposes it
        (None, V2, "v1"),
        # The child's own version is used only when consistent with the parent
        (V2, V2, "v2"),
        (V2, None, "v2"),
    ),
)
def test_resource_inherits_standard_version_from_package(
    package_schema, resource_schema, expected
):
    resource = {"name": "table", "path": "table.csv"}
    if resource_schema is not None:
        resource["$schema"] = resource_schema
    descriptor = {"resources": [resource]}
    if package_schema is not None:
        descriptor["$schema"] = package_schema
    package = Package.from_descriptor(descriptor)
    assert package.get_resource("table").standard_version == expected


@pytest.mark.parametrize(
    "resource_schema, schema_schema, expected",
    (
        (V2, V1, "v2"),
        (V1, V2, "v1"),
        (None, V2, "v1"),
        (V2, None, "v2"),
    ),
)
def test_schema_inherits_standard_version_from_resource(
    resource_schema, schema_schema, expected
):
    schema = {"fields": [{"name": "a", "type": "string"}]}
    if schema_schema is not None:
        schema["$schema"] = schema_schema
    descriptor = {"name": "table", "path": "table.csv", "schema": schema}
    if resource_schema is not None:
        descriptor["$schema"] = resource_schema
    resource = Resource.from_descriptor(descriptor)
    assert resource.schema.datapackage_version == expected


# # Inheritance through imperative (post-construction) attribution
# #
# # The same rule must hold when entities are wired together programmatically,
# # not only when built from a single descriptor. Inheritance is pushed down at
# # attach time (no pull, no back-ref); re-parenting re-runs the push, so the
# # child reflects its current parent. `basepath` rides the same mechanism.
#
#
# def test_resource_inherits_when_added_to_package():
#     resource = Resource.from_descriptor({"name": "t", "path": "t.csv", "$schema": V1})
#     assert resource.standard_version == "v1"
#     package = Package.from_descriptor({"$schema": V2, "resources": []})
#     package.add_resource(resource)
#     assert resource.standard_version == "v2"
#
#
# def test_resource_reflects_current_package_on_reparent():
#     resource = Resource.from_descriptor({"name": "t", "path": "t.csv", "$schema": V2})
#     Package.from_descriptor({"$schema": V1, "resources": []}).add_resource(resource)
#     assert resource.standard_version == "v1"
#     Package.from_descriptor({"$schema": V2, "resources": []}).add_resource(resource)
#     assert resource.standard_version == "v2"
#
#
# def test_schema_inherits_when_assigned_to_resource():
#     schema = Schema.from_descriptor(
#         {"$schema": V1, "fields": [{"name": "a", "type": "string"}]}
#     )
#     assert schema.standard_version == "v1"
#     resource = Resource.from_descriptor({"name": "t", "path": "t.csv", "$schema": V2})
#     resource.schema = schema
#     assert resource.schema.standard_version == "v2"
#
#
# def test_schema_from_separate_file_inherits_from_resource(tmp_path):
#     (tmp_path / "schema.json").write_text(
#         json.dumps({"$schema": V1, "fields": [{"name": "a", "type": "string"}]})
#     )
#     resource = Resource.from_descriptor(
#         {"name": "t", "path": "t.csv", "$schema": V2, "schema": "schema.json"},
#         basepath=str(tmp_path),
#     )
#     assert resource.schema.standard_version == "v2"
#
#
# # `basepath` inheritance (same push mechanism, opposite precedence)
# #
# # Unlike `standard_version` (where the parent always wins), a resource's own
# # basepath takes precedence over the one pushed down by its package.
#
#
# @pytest.mark.parametrize(
#     "resource_basepath, expected",
#     (
#         # No own basepath: inherit the package's
#         (None, "pkg"),
#         # Own basepath wins over the package's
#         ("own", "own"),
#     ),
# )
# def test_resource_inherits_basepath_from_package(resource_basepath, expected):
#     resource = Resource(path="t.csv", basepath=resource_basepath)
#     Package(basepath="pkg").add_resource(resource)
#     assert resource.basepath == expected
#
#
# def test_resource_basepath_reflects_current_package_on_reparent():
#     resource = Resource(path="t.csv")
#     Package(basepath="first").add_resource(resource)
#     assert resource.basepath == "first"
#     Package(basepath="second").add_resource(resource)
#     assert resource.basepath == "second"
>>>>>>> cc5edd81 (🔴 Infer datapackage version from $schema prop)
