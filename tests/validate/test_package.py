import json
import pytest
import pathlib
from copy import deepcopy
from frictionless import validate, helpers


# General


def test_validate_package():
    report = validate({"resources": [{"path": "data/table.csv"}]})
    assert report.valid


def test_validate_package_from_dict():
    with open("data/package/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/package")
        assert report.valid


def test_validate_package_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/invalid")
        assert report.flatten(
            ["taskPosition", "rowPosition", "fieldPosition", "code"]
        ) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key-error"],
            [2, 4, None, "blank-row"],
        ]


def test_validate_package_from_path():
    report = validate("data/package/datapackage.json")
    assert report.valid


def test_validate_package_from_path_invalid():
    report = validate("data/invalid/datapackage.json")
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key-error"],
        [2, 4, None, "blank-row"],
    ]


@pytest.mark.skip
@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_package_from_zip():
    report = validate("data/package.zip", type="package")
    assert report.valid


@pytest.mark.skip
@pytest.mark.skipif(helpers.is_platform("macos"), reason="It doesn't work for Macos")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_package_from_zip_invalid():
    report = validate("data/package-invalid.zip", type="package")
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key-error"],
        [2, 4, None, "blank-row"],
    ]


def test_validate_package_with_non_tabular():
    report = validate(
        {"resources": [{"path": "data/table.csv"}, {"path": "data/file.txt"}]},
    )
    assert report.valid


def test_validate_package_invalid_descriptor_path():
    report = validate("bad/datapackage.json")
    assert report.flatten(["code", "note"]) == [
        [
            "package-error",
            'cannot extract metadata "bad/datapackage.json" because "[Errno 2] No such file or directory: \'bad/datapackage.json\'"',
        ]
    ]


def test_validate_package_invalid_package():
    report = validate({"resources": [{"path": "data/table.csv", "schema": "bad"}]})
    assert report.flatten(["code", "note"]) == [
        [
            "schema-error",
            'cannot extract metadata "bad" because "[Errno 2] No such file or directory: \'bad\'"',
        ]
    ]


def test_validate_package_invalid_package_noinfer():
    report = validate({"resources": [{"path": "data/table.csv"}]}, noinfer=True)
    assert report.flatten(["code", "note"]) == [
        [
            "resource-error",
            '"{\'path\': \'data/table.csv\'} is not valid under any of the given schemas" at "" in metadata and at "oneOf" in profile',
        ]
    ]


def test_validate_package_invalid_table():
    report = validate({"resources": [{"path": "data/invalid.csv"}]})
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 3, "blank-label"],
        [None, 4, "duplicate-label"],
        [2, 3, "missing-cell"],
        [2, 4, "missing-cell"],
        [3, 3, "missing-cell"],
        [3, 4, "missing-cell"],
        [4, None, "blank-row"],
        [5, 5, "extra-cell"],
    ]


def test_validate_package_pathlib_source():
    report = validate(pathlib.Path("data/package/datapackage.json"))
    assert report.valid


def test_validate_package_infer():
    report = validate("data/infer/datapackage.json")
    assert report.valid


def test_validate_package_dialect_header_false():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["John", "22"], ["Alex", "33"], ["Paul", "44"]],
                "schema": {
                    "fields": [{"name": "name"}, {"name": "age", "type": "integer"}]
                },
                "layout": {"header": False},
            }
        ]
    }
    report = validate(descriptor)
    assert report.valid


def test_validate_package_with_schema_as_string():
    report = validate(
        {"resources": [{"path": "data/table.csv", "schema": "data/schema.json"}]}
    )
    assert report.valid


# Checksum

DESCRIPTOR_SH = {
    "resources": [
        {
            "name": "resource1",
            "path": "data/table.csv",
            "hashing": "sha256",
            "stats": {
                "hash": "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8",
                "bytes": 30,
            },
        }
    ]
}


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_package_checksum():
    source = deepcopy(DESCRIPTOR_SH)
    report = validate(source)
    assert report.valid


@pytest.mark.skip
def test_validate_package_checksum_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["bytes"] += 1
    source["resources"][0]["stats"]["hash"] += "a"
    report = validate(source)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "checksum-error"],
        [None, None, "checksum-error"],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_package_checksum_size():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("hash")
    report = validate(source)
    assert report.valid


@pytest.mark.skip
def test_validate_package_checksum_size_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"]["bytes"] += 1
    source["resources"][0]["stats"].pop("hash")
    report = validate(source)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "checksum-error"],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_package_checksum_hash():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    report = validate(source)
    assert report.valid


@pytest.mark.skip
def test_check_file_package_checksum_hash_invalid():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["stats"].pop("bytes")
    source["resources"][0]["stats"]["hash"] += "a"
    report = validate(source)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "checksum-error"],
    ]


def test_check_file_package_checksum_hash_not_supported_algorithm():
    source = deepcopy(DESCRIPTOR_SH)
    source["resources"][0]["hashing"] = "bad"
    source["resources"][0]["stats"].pop("bytes")
    report = validate(source)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, None, "hashing-error"],
    ]


# Integrity


DESCRIPTOR_FK = {
    "resources": [
        {
            "name": "cities",
            "data": [
                ["id", "name", "next_id"],
                [1, "london", 2],
                [2, "paris", 3],
                [3, "rome", 4],
                [4, "rio", None],
            ],
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "next_id", "type": "integer"},
                ],
                "foreignKeys": [
                    {"fields": "next_id", "reference": {"resource": "", "fields": "id"}},
                    {
                        "fields": "id",
                        "reference": {"resource": "people", "fields": "label"},
                    },
                ],
            },
        },
        {
            "name": "people",
            "data": [["label", "population"], [1, 8], [2, 2], [3, 3], [4, 6]],
        },
    ],
}


def test_validate_package_integrity_foreign_key_error():
    descriptor = deepcopy(DESCRIPTOR_FK)
    report = validate(descriptor)
    assert report.valid


def test_validate_package_integrity_foreign_key_not_defined():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["schema"]["foreignKeys"]
    report = validate(descriptor)
    assert report.valid


def test_validate_package_integrity_foreign_key_self_referenced_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][0]["data"][4]
    report = validate(descriptor)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [4, None, "foreign-key-error"],
    ]


@pytest.mark.skip
def test_validate_package_integrity_foreign_key_internal_resource_violation():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][1]["data"][4]
    report = validate(descriptor)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [5, None, "foreign-key-error"],
    ]


@pytest.mark.skip
def test_validate_package_integrity_foreign_key_internal_resource_violation_non_existent():
    descriptor = deepcopy(DESCRIPTOR_FK)
    descriptor["resources"][1]["data"] = [["label", "population"], [10, 10]]
    report = validate(descriptor)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, None, "foreign-key-error"],
        [3, None, "foreign-key-error"],
        [4, None, "foreign-key-error"],
        [5, None, "foreign-key-error"],
    ]


def test_validate_package_integrity_foreign_key_internal_resource_violation_with_nolookup():
    descriptor = deepcopy(DESCRIPTOR_FK)
    del descriptor["resources"][1]["data"][4]
    report = validate(descriptor, nolookup=True)
    assert report.valid


# Parallel


@pytest.mark.skip
@pytest.mark.ci
def test_validate_package_parallel_from_dict():
    with open("data/package/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/package", parallel=True)
        assert report.valid


@pytest.mark.skip
@pytest.mark.ci
def test_validate_package_parallel_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        report = validate(json.load(file), basepath="data/invalid", parallel=True)
        assert report.flatten(
            ["taskPosition", "rowPosition", "fieldPosition", "code"]
        ) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key-error"],
            [2, 4, None, "blank-row"],
        ]


@pytest.mark.skip
@pytest.mark.ci
def test_validate_package_with_parallel():
    report = validate("data/invalid/datapackage.json", parallel=True)
    assert report.flatten(["taskPosition", "rowPosition", "fieldPosition", "code"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key-error"],
        [2, 4, None, "blank-row"],
    ]


# Issues


def test_validate_package_mixed_issue_170():
    report = validate("data/infer/datapackage.json")
    assert report.valid


def test_validate_package_invalid_json_issue_192():
    report = validate("data/invalid.json", type="package")
    assert report.flatten(["code", "note"]) == [
        [
            "package-error",
            'cannot extract metadata "data/invalid.json" because "Expecting property name enclosed in double quotes: line 2 column 5 (char 6)"',
        ]
    ]


def test_validate_package_composite_primary_key_unique_issue_215():
    source = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "2"]],
                "schema": {
                    "fields": [{"name": "id1"}, {"name": "id2"}],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    report = validate(source)
    assert report.valid


@pytest.mark.skip
def test_validate_package_composite_primary_key_not_unique_issue_215():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["id1", "id2"], ["a", "1"], ["a", "1"]],
                "schema": {
                    "fields": [{"name": "id1"}, {"name": "id2"}],
                    "primaryKey": ["id1", "id2"],
                },
            }
        ],
    }
    report = validate(descriptor, skip_errors=["duplicate-row"])
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [3, None, "primary-key-error"],
    ]


def test_validate_package_geopoint_required_constraint_issue_231():
    # We check here that it doesn't raise exceptions
    report = validate("data/geopoint/datapackage.json")
    assert not report.valid


def test_validate_package_number_test_issue_232():
    # We check here that it doesn't raise exceptions
    report = validate("data/number/datapackage.json")
    assert not report.valid


def test_validate_package_with_schema_issue_348():
    descriptor = {
        "resources": [
            {
                "name": "people",
                "data": [
                    ["id", "name", "surname"],
                    ["p1", "Tom", "Hanks"],
                    ["p2", "Meryl", "Streep"],
                ],
                "schema": {
                    "fields": [
                        {"name": "id", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "surname", "type": "string"},
                        {"name": "dob", "type": "date"},
                    ]
                },
            }
        ]
    }
    report = validate(descriptor)
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [None, 4, "missing-label"],
        [2, 4, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


@pytest.mark.ci
def test_validate_package_uppercase_format_issue_494():
    with pytest.warns(UserWarning):
        report = validate("data/issue494.package.json")
        assert report.valid
        assert report.stats["tasks"] == 1
