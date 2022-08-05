import json
import pytest
import pathlib
from frictionless import Package, Checklist


# General


def test_validate_package():
    package = Package({"resources": [{"path": "data/table.csv"}]})
    report = package.validate()
    assert report.valid


def test_validate_package_from_dict():
    with open("data/package/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/package")
        report = package.validate()
        assert report.valid


def test_validate_package_from_dict_invalid():
    with open("data/invalid/datapackage.json") as file:
        package = Package(json.load(file), basepath="data/invalid")
        report = package.validate()
        assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
            [1, 3, None, "blank-row"],
            [1, 3, None, "primary-key"],
            [2, 4, None, "blank-row"],
        ]


def test_validate_package_from_path():
    package = Package("data/package/datapackage.json")
    report = package.validate()
    assert report.valid


def test_validate_package_from_path_invalid():
    package = Package("data/invalid/datapackage.json")
    report = package.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_validate_package_from_zip():
    package = Package("data/package.zip")
    report = package.validate()
    assert report.valid


def test_validate_package_from_zip_invalid():
    package = Package("data/package-invalid.zip")
    report = package.validate()
    assert report.flatten(["taskNumber", "rowNumber", "fieldNumber", "type"]) == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


def test_validate_package_with_non_tabular():
    package = Package(
        {
            "resources": [
                {"path": "data/table.csv"},
                {"path": "data/file.txt"},
            ]
        },
    )
    report = package.validate()
    assert report.valid


def test_validate_package_invalid_package_strict():
    package = Package({"resources": [{"path": "data/table.csv"}]})
    report = package.validate(strict=True)
    assert report.flatten(["type", "note"]) == [
        ["resource-error", 'property "name" is required in a strict mode'],
        ["resource-error", 'property "type" is required in a strict mode'],
        ["resource-error", 'property "scheme" is required in a strict mode'],
        ["resource-error", 'property "format" is required in a strict mode'],
        ["resource-error", 'property "encoding" is required in a strict mode'],
        ["resource-error", 'property "mediatype" is required in a strict mode'],
    ]


def test_validate_package_invalid_table():
    package = Package({"resources": [{"path": "data/invalid.csv"}]})
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
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
    package = Package(pathlib.Path("data/package/datapackage.json"))
    report = package.validate()
    assert report.valid


def test_validate_package_infer():
    package = Package("data/infer/datapackage.json")
    report = package.validate()
    assert report.valid


def test_validate_package_dialect_header_false():
    descriptor = {
        "resources": [
            {
                "name": "name",
                "data": [["John", "22"], ["Alex", "33"], ["Paul", "44"]],
                "dialect": {"header": False},
                "schema": {
                    "fields": [{"name": "name"}, {"name": "age", "type": "integer"}]
                },
            }
        ]
    }
    package = Package(descriptor)
    report = package.validate()
    assert report.valid


def test_validate_package_with_schema_as_string():
    package = Package(
        {"resources": [{"path": "data/table.csv", "schema": "data/schema.json"}]}
    )
    report = package.validate()
    assert report.valid


def test_validate_package_descriptor_type_package():
    package = Package("data/package/datapackage.json")
    report = package.validate()
    assert report.valid


def test_validate_package_descriptor_type_package_invalid():
    package = Package("data/invalid/datapackage.json")
    report = package.validate()
    assert report.flatten() == [
        [1, 3, None, "blank-row"],
        [1, 3, None, "primary-key"],
        [2, 4, None, "blank-row"],
    ]


# Bugs


def test_validate_package_mixed_issue_170():
    package = Package("data/infer/datapackage.json")
    report = package.validate()
    assert report.valid


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
    package = Package(source)
    report = package.validate()
    assert report.valid


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
    package = Package(descriptor)
    checklist = Checklist(skip_errors=["duplicate-row"])
    report = package.validate(checklist)
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, None, "primary-key"],
    ]


def test_validate_package_geopoint_required_constraint_issue_231():
    # We check here that it doesn't raise exceptions
    package = Package("data/geopoint/datapackage.json")
    report = package.validate()
    assert report.valid


def test_validate_package_number_test_issue_232():
    # We check here that it doesn't raise exceptions
    package = Package("data/number/datapackage.json")
    report = package.validate()
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
    package = Package(descriptor)
    report = package.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [None, 4, "missing-label"],
        [2, 4, "missing-cell"],
        [3, 4, "missing-cell"],
    ]


@pytest.mark.ci
@pytest.mark.vcr
def test_validate_package_uppercase_format_issue_494():
    package = Package("data/issue-494.package.json")
    report = package.validate()
    assert report.valid
    assert report.stats.tasks == 1


def test_validate_package_with_diacritic_symbol_issue_905():
    package = Package("data/issue-905/datapackage.json")
    report = package.validate()
    assert report.stats.tasks == 3


def test_validate_package_with_resource_data_is_a_string_issue_977():
    package = Package("data/issue-977.json")
    report = package.validate()
    assert report.flatten() == [
        [1, None, None, "resource-error"],
    ]


def test_validate_package_metadata_errors_with_missing_values_993():
    package = Package("data/package-with-missingvalues-993.json")
    error = package.list_metadata_errors()[0]
    assert error.type == "package-error"
    assert (
        error.note == '"missingValues" should be set as "resource.schema.missingValues"'
    )


def test_validate_package_metadata_errors_with_fields_993():
    package = Package("data/package-with-fields-993.json")
    error = package.list_metadata_errors()[0]
    assert error.type == "package-error"
    assert error.note == '"fields" should be set as "resource.schema.fields"'


def test_validate_package_errors_with_missing_values_993():
    package = Package("data/package-with-missingvalues-993.json")
    report = package.validate()
    assert report.flatten(["type", "message"]) == [
        [
            "package-error",
            'The data package has an error: "missingValues" should be set as "resource.schema.missingValues"',
        ]
    ]


def test_validate_package_errors_with_fields_993():
    package = Package("data/package-with-fields-993.json")
    report = package.validate()
    assert report.flatten(["type", "message"]) == [
        [
            "package-error",
            'The data package has an error: "fields" should be set as "resource.schema.fields"',
        ]
    ]
