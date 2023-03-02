from frictionless import Resource


def test_resource_datatype_directory():
    assert Resource("data/package").datatype == "package"


def test_resource_datatype_expandable():
    assert Resource("data/tables").datatype == "package"
    assert Resource("data/tables/*.csv").datatype == "package"
    assert Resource(["data/table.csv"]).datatype == "package"


def test_resource_datatype_adapter():
    #  assert Resource("https://github.com/datasets/oil-prices").datatype == "package"
    #  assert Resource("https://zenodo.org/record/6562498").datatype == "package"
    assert Resource("data/package.zip", packagify=True).datatype == "package"
    assert Resource("data/table.xlsx", packagify=True).datatype == "package"
    assert Resource("data/table.ods", packagify=True).datatype == "package"


def test_resource_datatype_path():
    assert Resource("data/table.csv").datatype == "table"
    assert Resource("data/file.txt").datatype == "file"
