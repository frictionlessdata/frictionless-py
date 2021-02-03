import pytest
from frictionless import Resource, helpers
from frictionless.plugins.html import HtmlDialect


# Read


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
    with Resource(source, dialect=dialect) as resource:
        assert resource.format == "html"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Write


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_html_parser_write(tmpdir):
    source = Resource("data/table.csv")
    target = source.write(str(tmpdir.join("table.html")))
    with target:
        assert target.header == ["id", "name"]
        assert target.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
