from frictionless import Catalog, Package


# General


def test_catalog():
    package = Package("data/package.json")
    catalog = Catalog(packages=[package])
    assert catalog.package_names == ["name"]
    assert catalog.to_descriptor() == {"packages": ["data/package.json"]}
