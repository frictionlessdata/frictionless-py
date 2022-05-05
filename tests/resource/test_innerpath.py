from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Innerpath


def test_resource_innerpath_local_csv_zip():
    with Resource("data/table.csv.zip") as resource:
        assert resource.innerpath == "table.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_innerpath_local_csv_zip_multiple_files():
    with Resource("data/table-multiple-files.zip", format="csv") as resource:
        assert resource.innerpath == "table-reverse.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "中国人"},
            {"id": 2, "name": "english"},
        ]


def test_resource_innerpath_local_csv_zip_multiple_files_explicit():
    with Resource("data/table-multiple-files.zip", innerpath="table.csv") as resource:
        assert resource.innerpath == "table.csv"
        assert resource.compression == "zip"
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
