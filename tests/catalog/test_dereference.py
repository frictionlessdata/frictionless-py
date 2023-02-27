from frictionless import Catalog


# General


def test_catalog_dereference():
    catalog = Catalog("data/dereference/catalog/datacatalog.yaml")
    catalog.get_dataset("name1").package.name = "package1"
    catalog.get_dataset("name2").package.name = "package2"
    assert catalog.to_descriptor() == {
        "name": "catalog",
        "datasets": [
            {"name": "name1", "package": "package1.yaml"},
            {"name": "name2", "package": "package2.yaml"},
        ],
    }
