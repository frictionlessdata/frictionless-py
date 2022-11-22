import os
import json
import yaml
import pytest
import yattag
from pathlib import Path
from zipfile import ZipFile
from frictionless import Schema, FrictionlessException


UNZIPPED_DIR = "data/fixtures/output-unzipped"
DESCRIPTOR = {
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
DESCRIPTOR_MIN = {
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "height", "type": "integer"},
    ]
}
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


def test_schema_to_copy():
    source = Schema.describe("data/table.csv")
    target = source.to_copy()
    assert source is not target
    assert source.to_descriptor() == target.to_descriptor()


def test_schema_to_json(tmpdir):
    output_file_path = str(tmpdir.join("schema.json"))
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    schema.to_json(output_file_path)
    with open(output_file_path, encoding="utf-8") as file:
        assert schema.to_descriptor() == json.load(file)


def test_schema_to_yaml(tmpdir):
    output_file_path = str(tmpdir.join("schema.yaml"))
    schema = Schema.from_descriptor(DESCRIPTOR_MIN)
    schema.to_yaml(output_file_path)
    with open(output_file_path, encoding="utf-8") as file:
        assert schema.to_descriptor() == yaml.safe_load(file)


# Summary


def test_schema_to_summary():
    schema = Schema.from_descriptor(DESCRIPTOR_MAX)
    output = schema.to_summary()
    assert (
        output.count("| name       | type    | required   |")
        and output.count("| id         | string  | True       |")
        and output.count("| height     | number  |            |")
        and output.count("| age        | integer |            |")
        and output.count("| name       | string  |            |")
    )


def test_schema_to_summary_without_required():
    descriptor = {
        "fields": [
            {"name": "test_1", "type": "string", "format": "default"},
            {"name": "test_2", "type": "string", "format": "default"},
            {"name": "test_3", "type": "string", "format": "default"},
        ]
    }
    schema = Schema.from_descriptor(descriptor)
    output = schema.to_summary()
    assert (
        output.count("| name   | type   | required   |")
        and output.count("| test_1 | string |            |")
        and output.count("| test_2 | string |            |")
        and output.count("| test_3 | string |            |")
    )


def test_schema_to_summary_with_type_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"name": "id", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
            {"name": "age", "format": "default"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(descriptor)
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.description == "Provided schema is not valid."


def test_schema_to_summary_with_name_missing_for_some_fields():
    descriptor = {
        "fields": [
            {"type": "integer", "format": "default"},
            {"type": "integer", "format": "default"},
            {"name": "name", "type": "string", "format": "default"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Schema.from_descriptor(descriptor)
    error = excinfo.value.error
    assert error.type == "schema-error"
    assert error.description == "Provided schema is not valid."


# Excel template


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
def test_schema_tableschema_to_excel_template(tmpdir, zip_path):
    # This code section was used from library tableschema-to-template
    # https://github.com/hubmapconsortium/tableschema-to-template/blob/main/tests/test_create_xlsx.py

    # zipfile.Path is introduced in Python3.8, and could make this cleaner:
    # xml_string = zipfile.Path(xlsx_path, zip_path).read_text()
    schema_path = "data/fixtures/schema.yaml"
    schema = Schema.from_descriptor(schema_path)
    xlsx_tmp_path = os.path.join(tmpdir, "template.xlsx")
    schema.to_excel_template(xlsx_tmp_path)
    with ZipFile(xlsx_tmp_path) as zip_handle:
        with zip_handle.open(zip_path) as file_handle:
            xml_string = file_handle.read().decode("utf-8")
    # Before Python3.8, attribute order is not stable in minidom,
    # so we need to use an outside library.
    pretty_xml = yattag.indent(xml_string)  # type: ignore
    pretty_xml_fixture_path = Path("data/fixtures/output-unzipped", zip_path)
    pretty_xml_tmp_path = Path(Path(tmpdir), Path(zip_path).name)
    pretty_xml_tmp_path.write_text(pretty_xml, encoding="utf-8")
    assert (
        pretty_xml.strip() == pretty_xml_fixture_path.read_text(encoding="utf-8").strip()
    )
