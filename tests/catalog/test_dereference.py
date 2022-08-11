from frictionless import Catalog


# General


def test_catalog_dereference():
    catalog = Catalog("data/dereference/catalog/datacatalog.yaml")
    catalog.get_package("package1").name = "package1"
    catalog.get_package("package2").name = "package2"
    assert catalog.to_descriptor() == {
        "name": "catalog",
        "packages": ["package1.yaml", "package2.yaml"],
    }
