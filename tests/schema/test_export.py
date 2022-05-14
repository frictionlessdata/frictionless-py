import os
import json
import yaml
import pytest
from pathlib import Path
from zipfile import ZipFile
from yaml import safe_load
from frictionless import Schema, describe_schema, helpers


DESCRIPTOR_MIN = {"fields": [{"name": "id"}, {"name": "height", "type": "integer"}]}


def test_schema_to_copy():
    source = describe_schema("data/table.csv")
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_schema_to_json(tmpdir):
    target = str(tmpdir.join("schema.json"))
    schema = Schema(DESCRIPTOR_MIN)
    schema.to_json(target)
    with open(target, encoding="utf-8") as file:
        assert schema == json.load(file)


def test_schema_to_yaml(tmpdir):
    target = str(tmpdir.join("schema.yaml"))
    schema = Schema(DESCRIPTOR_MIN)
    schema.to_yaml(target)
    with open(target, encoding="utf-8") as file:
        assert schema == yaml.safe_load(file)


def test_schema_from_jsonschema():
    schema = Schema.from_jsonschema("data/ecrin.json")
    assert schema == {
        "fields": [
            {"name": "file_type", "type": "string", "description": "always 'study'"},
            {
                "name": "id",
                "type": "integer",
                "description": "Internal accession number of the study within the MDR database",
                "constraints": {"required": True},
            },
            {
                "name": "display_title",
                "type": "string",
                "description": "By default the public or brief study title. If that is missing then the full scientific title, as used on the protocol document",
                "constraints": {"required": True},
            },
            {
                "name": "brief_description",
                "type": "object",
                "description": "Brief description, usually a few lines, of the study",
            },
            {
                "name": "data_sharing_statement",
                "type": "object",
                "description": "A statement from the sponsor and / or study leads about their intentions for IPD sharing",
            },
            {
                "name": "study_type",
                "type": "object",
                "description": "Categorisation of study type, e.g. 'Interventional', or 'Observational'",
            },
            {
                "name": "study_status",
                "type": "object",
                "description": "Categorisation of study status, e.g. 'Active, not recruiting', or 'Completed'",
            },
            {
                "name": "study_enrolment",
                "type": "integer",
                "description": "The anticipated or actual total number of participants in the clinical study.",
            },
            {
                "name": "study_gender_elig",
                "type": "object",
                "description": "Whether the study is open to all genders, or just male or female",
            },
            {
                "name": "min_age",
                "type": "object",
                "description": "The minimum age, if any, for a study participant",
            },
            {
                "name": "max_age",
                "type": "object",
                "description": "The maximum age, if any, for a study participant",
            },
            {"name": "study_identifiers", "type": "array"},
            {"name": "study_titles", "type": "array"},
            {"name": "study_features", "type": "array"},
            {"name": "study_topics", "type": "array"},
            {"name": "study_relationships", "type": "array"},
            {"name": "linked_data_objects", "type": "array"},
            {
                "name": "provenance_string",
                "type": "string",
                "description": "A listing of the source or sources (usually a trial registry) from which the data for the study has been drawn, and the date-time(s) when the data was last downloaded",
            },
        ]
    }


unzipped_dir = "data/fixtures/output-unzipped"


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
    schema_path = "data/fixtures/schema.yaml"
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
    pretty_xml_fixture_path = Path("data/fixtures/output-unzipped", zip_path)
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
    md_file_path = "data/fixtures/output-markdown/schema.md"
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
    md_file_path = "data/fixtures/output-markdown/schema-table.md"
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
    md_file_path = "data/fixtures/output-markdown/schema.md"
    with open(md_file_path, encoding="utf-8") as file:
        expected = file.read()
    target = str(tmpdir.join("schema.md"))
    schema = Schema(descriptor)
    schema.to_markdown(path=target).strip()
    with open(target, encoding="utf-8") as file:
        output = file.read()
    assert expected == output
