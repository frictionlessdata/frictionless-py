import pytest

from frictionless import Dialect, Package, Schema
from frictionless.resources.table import TableResource

DP_V2 = "https://datapackage.org/profiles/2.0/datapackage.json"
DR_V2 = "https://datapackage.org/profiles/2.0/dataresource.json"
TS_V2 = "https://datapackage.org/profiles/2.0/tableschema.json"
TD_V2 = "https://datapackage.org/profiles/2.0/tabledialect.json"


# Descriptor-level transformation


def test_upgrade_descriptor_package():
    descriptor = {
        "profile": "tabular-data-package",
        "name": "package",
        "resources": [
            {
                "name": "table",
                "profile": "tabular-data-resource",
                "path": "table.csv",
                "schema": {
                    # a `$schema` may be provided at the root only
                    "$schema": "https://datapackage.org/profiles/1.0/tableschema.json",
                    "fields": [{"name": "name", "type": "string"}],
                },
            },
            {"name": "other", "profile": "data-resource", "path": "other.csv"},
        ],
    }
    upgraded = Package._upgrade_descriptor(descriptor)

    # `$schema` as the first property, set to the canonical v2 profile
    assert list(upgraded)[0] == "$schema"
    assert upgraded["$schema"] == DP_V2
    assert upgraded.pop("$schema") == DP_V2
    assert upgraded == {
        "name": "package",
        "resources": [
            {
                "name": "table",
                "path": "table.csv",
                "type": "table",
                "schema": {"fields": [{"name": "name", "type": "string"}]},
            },
            {"name": "other", "path": "other.csv"},
        ],
    }


def test_upgrade_descriptor_custom_profile_urls():
    # a custom profile URL cannot be upgraded automatically: it is kept
    # (in `$schema` at the root, in `profile` on a child, where `$schema`
    # is not allowed)
    descriptor = {
        "$schema": "https://example.com/custom-package.json",
        "name": "package",
        "resources": [
            {"name": "other", "profile": "https://example.com/custom-resource.json"},
        ],
    }
    upgraded = Package._upgrade_descriptor(descriptor)
    assert upgraded["$schema"] == "https://example.com/custom-package.json"
    assert upgraded["resources"][0]["profile"] == "https://example.com/custom-resource.json"
    assert "$schema" not in upgraded["resources"][0]

    # the same, provided through the legacy `profile` property
    descriptor = {
        "profile": "https://example.com/custom-package.json",
        "name": "package",
        "resources": [],
    }
    upgraded = Package._upgrade_descriptor(descriptor)
    assert upgraded["$schema"] == "https://example.com/custom-package.json"


def test_upgrade_descriptor_standalone_classes():
    assert Package._upgrade_descriptor({"name": "p"})["$schema"] == DP_V2
    assert TableResource._upgrade_descriptor({"name": "t"})["$schema"] == DR_V2
    assert Schema._upgrade_descriptor({"fields": []})["$schema"] == TS_V2
    assert Dialect._upgrade_descriptor({})["$schema"] == TD_V2


# Instance upgrade


def test_upgrade_returns_new_instance():
    descriptor = {
        "name": "package",
        "resources": [
            {
                "name": "table",
                "profile": "tabular-data-resource",
                "path": "data/table.csv",
                "schema": {"fields": [{"name": "name", "type": "string"}]},
            },
        ],
    }
    package = Package(descriptor)
    upgraded = package.upgrade()

    # a new instance: the original is untouched (still v1)
    assert upgraded is not package
    assert package.to_descriptor().get("$schema") is None
    assert package.resources[0].profile == "tabular-data-resource"

    # the upgraded tree is v2, root-only `$schema`
    assert upgraded._schema_profile == DP_V2
    assert upgraded.resources[0].type == "table"
    assert upgraded.resources[0]._schema_profile is None
    assert upgraded.resources[0].schema._datapackage_version == "v2"
    assert upgraded.to_descriptor(validate=True)

    # idempotent
    assert upgraded.upgrade().to_descriptor() == upgraded.to_descriptor()


def test_upgrade_fixes_v1_invalid_names():
    # a name invalid per the v1 pattern ("My Package") is valid in v2
    package = Package.from_descriptor(
        {"name": "My Package", "resources": [{"name": "t", "path": "data/table.csv"}]},
        allow_invalid=True,
    )
    upgraded = package.upgrade()
    assert upgraded.name == "My Package"
    assert upgraded.to_descriptor(validate=True)


def test_upgrade_standalone_objects():
    schema = Schema({"fields": [{"name": "name", "type": "string"}]})
    upgraded = schema.upgrade()
    assert upgraded._schema_profile == TS_V2
    assert upgraded.to_descriptor()["$schema"] == TS_V2

    dialect = Dialect({"csv": {"delimiter": ";"}})
    assert dialect.upgrade()._schema_profile == TD_V2


# Export option


def test_to_descriptor_upgrade_option():
    descriptor = {
        "name": "package",
        "resources": [
            {
                "name": "table",
                "path": "data/table.csv",
                "schema": {"fields": [{"name": "name", "type": "string"}]},
            },
        ],
    }
    package = Package(descriptor)
    exported = package.to_descriptor(upgrade=True)

    # the instance is not mutated
    assert package.to_descriptor().get("$schema") is None

    # the exported tree is v2 and standalone-valid
    assert list(exported)[0] == "$schema"
    assert exported["$schema"] == DP_V2
    assert Package.validate_descriptor(exported).valid
    assert package.to_descriptor(validate=True, upgrade=True) == exported
