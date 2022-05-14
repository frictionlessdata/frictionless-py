import io
import os
import json
import pytest
import requests
from pathlib import Path
from zipfile import ZipFile
from yaml import safe_load
from decimal import Decimal
from frictionless import Schema, helpers
from frictionless import FrictionlessException


BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"
DESCRIPTOR_MIN = {"fields": [{"name": "id"}, {"name": "height", "type": "integer"}]}
DESCRIPTOR_MAX = {
    "fields": [
        {"name": "id", "type": "string", "constraints": {"required": True}},
        {"name": "height", "type": "number"},
        {"name": "age", "type": "integer"},
        {"name": "name", "type": "string"},
        {"name": "occupation", "type": "string"},
    ],
    "primaryKey": ["id"],
    "foreignKeys": [
        {"fields": ["name"], "reference": {"resource": "", "fields": ["id"]}}
    ],
    "missingValues": ["", "-", "null"],
}


# General


def test_schema():
    assert Schema(DESCRIPTOR_MIN)
    assert Schema(DESCRIPTOR_MAX)
    assert Schema("data/schema-valid-full.json")
    assert Schema("data/schema-valid-simple.json")


def test_schema_extract_metadata_error():
    with pytest.raises(FrictionlessException):
        Schema([])


def test_schema_metadata_invalid():
    schema = Schema("data/schema-invalid-multiple-errors.json")
    assert len(schema.metadata_errors) == 5


def test_schema_descriptor():
    assert Schema(DESCRIPTOR_MIN) == DESCRIPTOR_MIN
    assert Schema(DESCRIPTOR_MAX) == DESCRIPTOR_MAX


def test_schema_descriptor_path():
    path = "data/schema-valid-simple.json"
    actual = Schema(path)
    with io.open(path, encoding="utf-8") as file:
        expect = json.load(file)
    assert actual == expect


@pytest.mark.vcr
def test_schema_descriptor_url():
    url = BASEURL % "data/schema.json"
    actual = Schema(url)
    expect = requests.get(url).json()
    assert actual == expect


def test_schema_read_cells():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_null_values():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "", "-", "string", "null"]
    target = ["string", None, None, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_too_short():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string"]
    target = ["string", Decimal(10.0), 1, "string", None]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_too_long():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "10.0", "1", "string", "string", "string"]
    target = ["string", Decimal(10.0), 1, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target


def test_schema_read_cells_wrong_type():
    schema = Schema(DESCRIPTOR_MAX)
    source = ["string", "notdecimal", "10.6", "string", "string"]
    target = ["string", None, None, "string", "string"]
    cells, notes = schema.read_cells(source)
    assert cells == target
    assert notes[1] == {"type": 'type is "number/default"'}
    assert notes[2] == {"type": 'type is "integer/default"'}


def test_schema_missing_values():
    assert Schema(DESCRIPTOR_MIN).missing_values == [""]
    assert Schema(DESCRIPTOR_MAX).missing_values == ["", "-", "null"]


def test_schema_fields():
    expect = ["id", "height"]
    actual = [field.name for field in Schema(DESCRIPTOR_MIN).fields]
    assert expect == actual


def test_schema_get_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.get_field("id").name == "id"
    assert schema.get_field("height").name == "height"


def test_schema_get_field_error_not_found():
    schema = Schema(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.get_field("bad")
    error = excinfo.value.error
    assert error.code == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_update_field():
    schema = Schema(DESCRIPTOR_MIN)
    schema.get_field("id")["type"] = "number"
    schema.get_field("height")["type"] = "number"
    assert schema.get_field("id").type == "number"
    assert schema.get_field("height").type == "number"


def test_schema_has_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.has_field("id")
    assert schema.has_field("height")
    assert not schema.has_field("undefined")


def test_schema_remove_field():
    schema = Schema(DESCRIPTOR_MIN)
    assert schema.remove_field("height")
    assert schema.field_names == ["id"]


def test_schema_remove_field_error_not_found():
    schema = Schema(DESCRIPTOR_MIN)
    with pytest.raises(FrictionlessException) as excinfo:
        schema.remove_field("bad")
    error = excinfo.value.error
    assert error.code == "schema-error"
    assert error.note == 'field "bad" does not exist'


def test_schema_field_names():
    assert Schema(DESCRIPTOR_MIN).field_names == ["id", "height"]


def test_schema_primary_key():
    assert Schema(DESCRIPTOR_MIN).primary_key == []
    assert Schema(DESCRIPTOR_MAX).primary_key == ["id"]


def test_schema_foreign_keys():
    assert Schema(DESCRIPTOR_MIN).foreign_keys == []
    assert Schema(DESCRIPTOR_MAX).foreign_keys == DESCRIPTOR_MAX["foreignKeys"]


def test_schema_add_then_remove_field():
    schema = Schema()
    schema.add_field({"name": "name"})
    field = schema.remove_field("name")
    assert field.name == "name"


def test_schema_primary_foreign_keys_as_array():
    descriptor = {
        "fields": [{"name": "name"}],
        "primaryKey": ["name"],
        "foreignKeys": [
            {
                "fields": ["parent_id"],
                "reference": {"resource": "resource", "fields": ["id"]},
            }
        ],
    }
    schema = Schema(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


def test_schema_primary_foreign_keys_as_string():
    descriptor = {
        "fields": [{"name": "name"}],
        "primaryKey": "name",
        "foreignKeys": [
            {"fields": "parent_id", "reference": {"resource": "resource", "fields": "id"}}
        ],
    }
    schema = Schema(descriptor)
    assert schema.primary_key == ["name"]
    assert schema.foreign_keys == [
        {"fields": ["parent_id"], "reference": {"resource": "resource", "fields": ["id"]}}
    ]


def test_schema_metadata_valid():
    assert Schema("data/schema-valid-simple.json").metadata_valid
    assert Schema("data/schema-valid-full.json").metadata_valid
    assert Schema("data/schema-valid-pk-array.json").metadata_valid
    assert Schema("data/schema-valid-fk-array.json").metadata_valid


def test_schema_metadata_not_valid():
    assert not Schema("data/schema-invalid-empty.json").metadata_valid
    assert not Schema("data/schema-invalid-pk-string.json").metadata_valid
    assert not Schema("data/schema-invalid-pk-array.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-string.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-no-reference.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-array.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-string-array-ref.json").metadata_valid
    assert not Schema("data/schema-invalid-fk-array-string-ref.json").metadata_valid


def test_schema_metadata_not_valid_multiple_errors():
    schema = Schema("data/schema-invalid-multiple-errors.json")
    assert len(schema.metadata_errors) == 5


def test_schema_metadata_not_valid_multiple_errors_with_pk():
    schema = Schema("data/schema-invalid-pk-is-wrong-type.json")
    assert len(schema.metadata_errors) == 3


def test_schema_metadata_error_message():
    schema = Schema({"fields": [{"name": "name", "type": "other"}]})
    note = schema.metadata_errors[0]["note"]
    assert len(schema.metadata_errors) == 1
    assert "is not valid" in note
    assert "{'name': 'name', 'type': 'other'}" in note
    assert "is not valid under any of the given schema" in note


def test_schema_valid_examples():
    schema = Schema(
        {
            "fields": [
                {"name": "name", "type": "string", "example": "John"},
                {"name": "age", "type": "integer", "example": 42},
            ]
        }
    )
    assert schema.get_field("name").example == "John"
    assert len(schema.metadata_errors) == 0


def test_schema_invalid_example():
    schema = Schema(
        {
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "example": None,
                    "constraints": {"required": True},
                }
            ]
        }
    )
    note = schema.metadata_errors[0]["note"]
    assert len(schema.metadata_errors) == 1
    assert 'example value for field "name" is not valid' == note


@pytest.mark.parametrize("create_descriptor", [(False,), (True,)])
def test_schema_standard_specs_properties(create_descriptor):
    options = dict(
        fields=[],
        missing_values=[],
        primary_key=[],
        foreign_keys=[],
    )
    schema = (
        Schema(**options)
        if not create_descriptor
        else Schema(helpers.create_descriptor(**options))
    )
    assert schema.fields == []
    assert schema.missing_values == []
    assert schema.primary_key == []
    assert schema.foreign_keys == []


# Issues


def test_schema_field_date_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "date", "format": "%d/%m/%y"}]}
    schema = Schema(descriptor)
    assert schema


def test_schema_field_time_format_issue_177():
    descriptor = {"fields": [{"name": "myfield", "type": "time", "format": "%H:%M:%S"}]}
    schema = Schema(descriptor)
    assert schema


def test_schema_add_remove_field_issue_218():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    test_schema = Schema(descriptor)
    test_schema.remove_field("test_1")
    test_schema.add_field({"name": "test_4", "type": "string", "format": "default"})


def test_schema_not_supported_type_issue_goodatbles_304():
    schema = Schema({"fields": [{"name": "name"}, {"name": "age", "type": "bad"}]})
    assert schema.metadata_valid is False
    assert schema.fields[1] == {"name": "age", "type": "bad"}


unzipped_dir = "tests/fixtures/output-unzipped"


@pytest.mark.parametrize(
    "zip_path",
    [
        "docProps/app.xml",
        "xl/comments1.xml",
        "xl/sharedStrings.xml",
        "xl/styles.xml",
        "xl/workbook.xml",
        "xl/drawings/vmlDrawing1.vml",
        "xl/theme/theme1.xml",
        "xl/worksheets/sheet1.xml",
        "xl/worksheets/sheet2.xml",
        "xl/worksheets/sheet3.xml",
        "xl/worksheets/_rels/sheet1.xml.rels",
        "xl/_rels/workbook.xml.rels",
        "_rels/.rels",
    ],
)
def test_schema_tableschema_to_excel_584(tmpdir, zip_path):
    # This code section was used from library tableschema-to-template
    # https://github.com/hubmapconsortium/tableschema-to-template/blob/main/tests/test_create_xlsx.py

    # zipfile.Path is introduced in Python3.8, and could make this cleaner:
    # xml_string = zipfile.Path(xlsx_path, zip_path).read_text()
    schema_path = "tests/fixtures/schema.yaml"
    schema = Schema(safe_load(schema_path))
    xlsx_tmp_path = os.path.join(tmpdir, "template.xlsx")
    schema.to_excel_template(xlsx_tmp_path)
    with ZipFile(xlsx_tmp_path) as zip_handle:
        with zip_handle.open(zip_path) as file_handle:
            xml_string = file_handle.read().decode("utf-8")
    # Before Python3.8, attribute order is not stable in minidom,
    # so we need to use an outside library.
    yattag = helpers.import_from_plugin("yattag", plugin="excel")
    pretty_xml = yattag.indent(xml_string)
    pretty_xml_fixture_path = Path("tests/fixtures/output-unzipped", zip_path)
    pretty_xml_tmp_path = Path(Path(tmpdir), Path(zip_path).name)
    pretty_xml_tmp_path.write_text(pretty_xml, encoding="utf-8")
    assert (
        pretty_xml.strip() == pretty_xml_fixture_path.read_text(encoding="utf-8").strip()
    )


def test_schema_pprint_1029():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    schema = Schema(descriptor)
    expected = """{'fields': [{'format': 'default', 'name': 'test_1', 'type': 'string'},
            {'format': 'default', 'name': 'test_2', 'type': 'string'},
            {'format': 'default', 'name': 'test_3', 'type': 'string'}]}"""
    assert repr(schema) == expected


def test_schema_to_markdown_837(tmpdir):
    descriptor = {
        "fields": [
            {
                "name": "id",
                "description": "Any positive integer",
                "type": "integer",
                "constraints": {"minimum": 1},
            },
            {
                "name": "age",
                "title": "Age",
                "description": "Any number >= 1",
                "type": "number",
                "constraints": {"minimum": 1},
            },
        ]
    }
    schema = Schema(descriptor)
    md_file_path = "tests/fixtures/output-markdown/schema.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert schema.to_markdown().strip() == expected


def test_schema_to_markdown_table_837():
    descriptor = {
        "fields": [
            {
                "name": "id",
                "description": "Any positive integer",
                "type": "integer",
                "constraints": {"minimum": 1},
            },
            {
                "name": "age",
                "title": "Age",
                "description": "Any number >= 1",
                "type": "number",
                "constraints": {"minimum": 1},
            },
        ]
    }
    schema = Schema(descriptor)
    md_file_path = "tests/fixtures/output-markdown/schema-table.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    assert schema.to_markdown(table=True).strip() == expected


def test_schema_to_markdown_file_837(tmpdir):
    descriptor = {
        "fields": [
            {
                "name": "id",
                "description": "Any positive integer",
                "type": "integer",
                "constraints": {"minimum": 1},
            },
            {
                "name": "age",
                "title": "Age",
                "description": "Any number >= 1",
                "type": "number",
                "constraints": {"minimum": 1},
            },
        ]
    }
    md_file_path = "tests/fixtures/output-markdown/schema.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    target = str(tmpdir.join("schema.md"))
    schema = Schema(descriptor)
    schema.to_markdown(path=target).strip()
    with open(target, encoding="utf-8") as file:
        output = file.read()
    assert expected == output
