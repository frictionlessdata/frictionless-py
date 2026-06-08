import pytest

from frictionless import Dialect, Metadata, Package, Resource, Schema, settings

# General


def test_metadata():
    descriptor = Metadata.metadata_retrieve({"key": "value"})
    assert descriptor["key"] == "value"


def test_metadata_from_path():
    descriptor = Metadata.metadata_retrieve("data/schema-valid.json")
    assert descriptor["primaryKey"] == "id"


# Data package version inference from `$schema` prop


@pytest.mark.parametrize(
    "Entity, descriptor",
    (
        (Package, {"resources": []}),
        (Schema, {"fields": []}),
        (Resource, {"name": "table", "path": "table.csv"}),
    ),
    ids=["package", "schema", "resource"],
)
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
def test_datapackage_version_inferred_from_schema(Entity, descriptor, schema, expected):
    # Test only for direct inference from the class `$schema` property,
    # not inheritance
    descriptor = dict(descriptor)
    if schema is not None:
        descriptor["$schema"] = schema
    metadata = Entity.from_descriptor(descriptor)
    assert metadata.datapackage_version == expected


# `$schema` (de)serialization

SCHEMA_PROFILE = "https://datapackage.org/profiles/2.0/datapackage.json"


@pytest.mark.parametrize(
    "Entity, descriptor",
    (
        (Package, {"resources": []}),
        (Schema, {"fields": []}),
        (Resource, {"name": "table", "path": "table.csv"}),
        (Dialect, {}),
    ),
    ids=["package", "schema", "resource", "dialect"],
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
        (Dialect, {}),
    ),
    ids=["package", "schema", "resource", "dialect"],
)
def test_schema_profile_exported_to_descriptor(Entity, kwargs):
    metadata = Entity(schema_profile=SCHEMA_PROFILE, **kwargs)
    assert metadata.to_descriptor()["$schema"] == SCHEMA_PROFILE


# Inheritance from a parent entity

V1 = "https://datapackage.org/profiles/1.0/datapackage.json"
V2 = "https://datapackage.org/profiles/2.0/datapackage.json"


@pytest.mark.parametrize(
    "Parent, descriptor, get_child",
    (
        (
            Package,
            {"resources": [{"name": "table", "path": "table.csv"}]},
            lambda parent: parent.get_resource("table"),
        ),
        (
            Resource,
            {"name": "table", "path": "table.csv", "schema": {"fields": []}},
            lambda parent: parent.schema,
        ),
        (
            Resource,
            {"name": "table", "path": "table.csv", "dialect": {"header": False}},
            lambda parent: parent.dialect,
        ),
    ),
    ids=["package->resource", "resource->schema", "resource->dialect"],
)
@pytest.mark.parametrize(
    "parent_schema, expected",
    (
        (V1, "v1"),
        (V2, "v2"),
        # Absent `$schema`: the spec mandates v1 as the default
        (None, "v1"),
    ),
)
def test_child_inherits_standard_version_from_parent(
    Parent, descriptor, get_child, parent_schema, expected
):
    # A child with no `$schema` of its own inherits the version
    # resolved by its parent.
    descriptor = dict(descriptor)
    if parent_schema is not None:
        descriptor["$schema"] = parent_schema

    parent = Parent.from_descriptor(descriptor)
    assert get_child(parent).datapackage_version == expected


@pytest.mark.parametrize("package_schema, expected", ((V1, "v1"), (V2, "v2")))
def test_standard_version_inheritance_is_transitive(package_schema, expected):
    # A `$schema` on the package propagates down to a resource's
    # schema and dialect, even though neither carries its own `$schema`.
    package = Package.from_descriptor(
        {
            "$schema": package_schema,
            "resources": [
                {
                    "name": "table",
                    "path": "table.csv",
                    "schema": {"fields": []},
                    "dialect": {"header": False},
                }
            ],
        }
    )
    resource = package.get_resource("table")
    assert resource.datapackage_version == expected
    assert resource.schema.datapackage_version == expected
    assert resource.dialect.datapackage_version == expected


def test_resource_added_to_package_inherits_standard_version():
    # A resource added programmatically (not via descriptor import)
    # should still inherit the package's standard version.
    package = Package.from_descriptor({"$schema": V2, "resources": []})
    resource = package.add_resource(Resource(name="table", path="table.csv"))
    assert resource.datapackage_version == "v2"


@pytest.mark.parametrize(
    "Parent, descriptor, attr, make_value, get_child",
    (
        (
            Package,
            {"resources": []},
            "resources",
            lambda: [Resource(name="table", path="table.csv")],
            lambda parent: parent.get_resource("table"),
        ),
        (
            Resource,
            {"name": "t", "path": "t.csv"},
            "schema",
            lambda: Schema.from_descriptor({"fields": []}),
            lambda parent: parent.schema,
        ),
        (
            Resource,
            {"name": "t", "path": "t.csv"},
            "dialect",
            lambda: Dialect.from_descriptor({"header": False}),
            lambda parent: parent.dialect,
        ),
    ),
    ids=["package.resources", "resource.schema", "resource.dialect"],
)
@pytest.mark.parametrize("parent_schema, expected", ((V1, "v1"), (V2, "v2")))
def test_child_assigned_to_parent_inherits_standard_version(
    Parent, descriptor, attr, make_value, get_child, parent_schema, expected
):
    # A child set via direct attribute assignment (`parent.<attr> = ...`)
    # should inherit the parent's standard version, just like on import.
    parent = Parent.from_descriptor({**descriptor, "$schema": parent_schema})
    setattr(parent, attr, make_value())
    assert get_child(parent).datapackage_version == expected


@pytest.mark.parametrize(
    "attr, path",
    (("schema", "schema.json"), ("dialect", "dialect.json")),
    ids=["resource.schema", "resource.dialect"],
)
def test_child_assigned_as_path_inherits_standard_version(attr, path):
    # Assigning a *path* (a lazy descriptor resolved by the getter) should also
    # inherit: the version is pushed in when the getter materializes the child.
    resource = Resource.from_descriptor(
        {"$schema": V2, "name": "t", "path": "t.csv"}, basepath="data"
    )
    setattr(resource, attr, path)
    assert getattr(resource, attr).datapackage_version == "v2"


@pytest.mark.parametrize(
    "make_parent, get_child",
    (
        (
            lambda: Package(
                resources=[Resource(name="t", path="t.csv")], schema_profile=V2
            ),
            lambda parent: parent.get_resource("t"),
        ),
        (
            lambda: Resource(
                name="t",
                path="t.csv",
                schema=Schema.from_descriptor({"fields": []}),
                schema_profile=V2,
            ),
            lambda parent: parent.schema,
        ),
        (
            lambda: Resource(
                name="t",
                path="t.csv",
                dialect=Dialect.from_descriptor({"header": False}),
                schema_profile=V2,
            ),
            lambda parent: parent.dialect,
        ),
    ),
    ids=["package.resources", "resource.schema", "resource.dialect"],
)
def test_child_constructed_with_parent_inherits_standard_version(make_parent, get_child):
    # Pre-built children passed to the constructor (not via `from_descriptor`)
    # should inherit the parent's standard version.
    assert get_child(make_parent()).datapackage_version == "v2"
