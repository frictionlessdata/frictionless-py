import pytest
from frictionless import Table, helpers
from frictionless.plugins.html import HtmlDialect


# Parser


@pytest.mark.parametrize(
    "source, selector",
    [
        ("data/table1.html", "table"),
        ("data/table2.html", "table"),
        ("data/table3.html", ".mememe"),
        ("data/table4.html", ""),
    ],
)
def test_html_parser(source, selector):
    dialect = HtmlDialect(selector=selector)
    with Table(source, dialect=dialect) as table:
        assert table.format == "html"
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_html_parser_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.html"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
