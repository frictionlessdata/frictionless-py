from frictionless import Resource, formats


# Read


def test_parquet_parser():
    with Resource("data/table.parq") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_parquet_parser_columns():
    control = formats.ParquetControl(columns=["id"])
    with Resource("data/table.parq", control=control) as resource:
        assert resource.header == ["id"]
        assert resource.read_rows() == [
            {"id": 1},
            {"id": 2},
        ]
