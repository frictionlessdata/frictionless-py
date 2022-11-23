import os
import yattag
import pytest
from pathlib import Path
from zipfile import ZipFile
from frictionless import Schema


# Schema


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
