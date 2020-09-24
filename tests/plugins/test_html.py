import pytest
from frictionless import Table
from frictionless.plugins.html import HtmlDialect


# Parser (read)


@pytest.mark.parametrize(
    "source, selector",
    [
        ("data/table1.html", "table"),
        ("data/table2.html", "table"),
        ("data/table3.html", ".mememe"),
        ("data/table4.html", ""),
    ],
)
def test_table_html(source, selector):
    dialect = HtmlDialect(selector=selector)
    with Table(source, dialect=dialect) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


# Parser (write)


def test_table_html_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.html"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
