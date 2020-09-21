from frictionless import Table


# Parser


def test_table_format_tsv():
    with Table("data/table.tsv") as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [
            ["1", "english"],
            ["2", "中国人"],
            ["3", None],
        ]


def test_table_tsv_write(tmpdir):
    source = "data/table.csv"
    target = str(tmpdir.join("table.tsv"))
    with Table(source) as table:
        table.write(target)
    with Table(target) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]
