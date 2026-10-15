from frictionless import Package, Resource, Schema

# A custom `$schema` URL — the v2 way to point at a profile — makes the Data
# Package version known to nobody but the profile's author: it resolves to
# "unknown", and version gates then accept a superset of v1 and v2 (instead
# of guessing a standard version). A legacy `profile` is a v1-only property:
# a descriptor using it is explicitly v1, whatever the profile value.

CUSTOM = "https://example.com/my-profile.json"

V1_PROFILE = "https://datapackage.org/profiles/1.0/datapackage.json"
V2_PROFILE = "https://datapackage.org/profiles/2.0/datapackage.json"


# Version resolution


def test_custom_profile_resolves_to_unknown_version():
    # a `$schema` pointing outside the datapackage.org profiles
    assert Package.effective_datapackage_version({"$schema": CUSTOM}, None) == "unknown"

    # a legacy `profile` (standards v1) is a v1-only property: any value —
    # including a custom profile URL — keeps the descriptor explicitly v1
    assert Package.effective_datapackage_version({"profile": "data-package"}, None) == "v1"
    assert (
        Package.effective_datapackage_version({"profile": "tabular-data-package"}, None)
        == "v1"
    )
    assert (
        Resource.effective_datapackage_version({"profile": "data-resource"}, None) == "v1"
    )
    assert (
        Package.effective_datapackage_version({"profile": CUSTOM}, None) == "v1"
    )
    assert (
        Package.effective_datapackage_version(
            {"profile": "data/custom-profile.json"}, None
        )
        == "v1"
    )

    # standard profiles and an absent `$schema` are unaffected
    assert Package.effective_datapackage_version({"$schema": V1_PROFILE}, None) == "v1"
    assert Package.effective_datapackage_version({"$schema": V2_PROFILE}, None) == "v2"
    assert Package.effective_datapackage_version({}, None) == "v1"


def test_unknown_version_is_inherited_top_down():
    # an ancestor's resolved version wins (a descendant cannot escape it):
    # "unknown" is imposed on the children like any other version
    assert (
        Resource.effective_datapackage_version({"profile": CUSTOM}, "v1") == "v1"
    )
    assert (
        Resource.effective_datapackage_version({"$schema": V2_PROFILE}, "unknown")
        == "unknown"
    )


# Superset of v1 and v2

SUPERSET_DESCRIPTOR = {
    "$schema": CUSTOM,
    "name": "My Package",  # invalid per the v1 pattern
    "resources": [
        {
            "name": "My Table",  # invalid per the v1 pattern
            "data": [["name"], [1], [2]],
            "schema": {
                "fields": [
                    # `exclusiveMinimum` is a v2-only constraint
                    {"name": "name", "type": "integer", "constraints": {"exclusiveMinimum": 0}},
                ],
                # the object form is a v2-only feature
                "missingValues": [{"value": "-99", "label": "REFUSED"}],
            },
        }
    ],
}


def test_custom_profile_accepts_superset():
    report = Package.validate_descriptor(SUPERSET_DESCRIPTOR)
    assert report.flatten(["type", "note"]) == []
    assert report.valid

    package = Package(SUPERSET_DESCRIPTOR)
    resource = package.get_table_resource("My Table")
    assert resource._datapackage_version == "unknown"
    assert resource.schema._datapackage_version == "unknown"

    # the detached child keeps the unknown (permissive) version
    assert resource.validate().valid
    assert resource.to_copy()._datapackage_version == "unknown"


def test_legacy_profile_property_is_explicit_v1():
    # a custom profile referenced through the legacy `profile` property
    # (fetched for validation — hence a real file) is a v1-era profile: the
    # descriptor stays explicitly v1, and the version gates stay strict
    descriptor = {
        "profile": "data/custom-profile.json",
        "name": "p",
        "resources": [
            {
                "name": "r",
                "data": [["name"], ["a"]],
                "schema": {
                    "fields": [{"name": "name", "type": "string"}],
                    "missingValues": [{"value": "-99", "label": "REFUSED"}],
                },
            }
        ],
    }
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["schema-error", "missing values in object form require datapackage v2"]
    ]

    # the import refuses the invalid descriptor; importing despite the
    # errors confirms the explicit v1 resolution
    package = Package.from_descriptor(descriptor, allow_invalid=True)
    assert package.get_table_resource("r")._datapackage_version == "v1"


def test_child_cannot_escape_v1_with_a_custom_profile():
    # a v1 package (an absent `$schema`) imposes v1 on a resource whose own
    # profile is custom: the version gates stay strict
    descriptor = {
        "name": "p",
        "resources": [
            {
                "name": "r",
                "profile": CUSTOM,
                "path": "data/table.csv",
                "schema": {
                    "fields": [{"name": "f", "type": "string"}],
                    "missingValues": [{"value": "-99"}],
                },
            }
        ],
    }
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        ["schema-error", "missing values in object form require datapackage v2"]
    ]


def test_standalone_custom_schema_is_permissive():
    schema = Schema(
        {
            "$schema": CUSTOM,
            "fields": [
                {"name": "n", "type": "integer", "constraints": {"exclusiveMinimum": 0}}
            ],
        }
    )
    assert schema._datapackage_version == "unknown"
    assert schema.to_descriptor(validate=True)

    resource = Resource.from_descriptor(
        {
            "$schema": CUSTOM,
            "name": "My Resource",
            "data": [["f"], [1]],
            "schema": {
                "fields": [
                    {"name": "f", "type": "integer", "constraints": {"exclusiveMinimum": 0}}
                ],
            },
        }
    )
    assert resource._datapackage_version == "unknown"
    assert resource.validate().valid


def test_upgrade_keeps_custom_profile_version_unknown():
    upgraded = Package(SUPERSET_DESCRIPTOR).upgrade()
    # the custom `$schema` is kept as-is (an automatic upgrade of a custom
    # profile is not possible), so the version stays unknown (permissive)
    assert upgraded._schema_profile == CUSTOM
    assert upgraded.resources[0]._datapackage_version == "unknown"
    assert upgraded.validate().valid
