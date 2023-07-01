import pytest

from frictionless import Resource, resources

# File


@pytest.mark.parametrize(
    "source",
    [
        "data/document.pdf",
    ],
)
def test_resource_datatype_file(source):
    resource = Resource(source)
    assert resource.datatype == "document"
    assert isinstance(resource, resources.FileResource)


# Text


@pytest.mark.parametrize(
    "source",
    [
        "data/text.txt",
    ],
)
def test_resource_datatype_text(source):
    resource = Resource(source)
    assert resource.datatype == "text"
    assert isinstance(resource, resources.TextResource)


# Article


@pytest.mark.parametrize(
    "source",
    [
        "data/article.md",
    ],
)
def test_resource_datatype_article(source):
    resource = Resource(source)
    assert resource.datatype == "article"
    assert isinstance(resource, resources.ArticleResource)


# Script


@pytest.mark.parametrize(
    "source",
    [
        "data/script.py",
    ],
)
def test_resource_datatype_script(source):
    resource = Resource(source)
    assert resource.datatype == "script"
    assert isinstance(resource, resources.ScriptResource)


# Json


@pytest.mark.parametrize(
    "source",
    [
        "data/table.json",
    ],
)
def test_resource_datatype_json(source):
    resource = Resource(source)
    assert resource.datatype == "json"
    assert isinstance(resource, resources.JsonResource)


# Table


@pytest.mark.parametrize(
    "source",
    [
        "data/table.csv",
        "data/table.xlsx",
        "data/table.ods",
    ],
)
def test_resource_datatype_table(source):
    resource = Resource(source)
    assert resource.datatype == "table"
    assert isinstance(resource, resources.TableResource)


# Package


@pytest.mark.parametrize(
    "source",
    [
        "data/package",
        "data/tables",
        "data/tables/*.csv",
        ["data/table.csv"],
        # TODO: use vcr here
        #  "http://ckan:5000/dataset/name",
        #  "https://github.com/datasets/oil-prices",
        #  "https://zenodo.org/record/6562498",
    ],
)
def test_resource_datatype_package(source):
    resource = Resource(source)
    assert resource.datatype == "package"
    assert isinstance(resource, resources.PackageResource)


@pytest.mark.parametrize(
    "source",
    [
        "data/package.zip",
        "data/table.xlsx",
        "data/table.ods",
    ],
)
def test_resource_datatype_package_with_packagify(source):
    resource = Resource(source, packagify=True)
    assert resource.datatype == "package"
    assert isinstance(resource, resources.PackageResource)
