from frictionless import Package, Resource, describe

# General


def test_describe_resource():
    resource = describe("data/table.csv")
    assert isinstance(resource, Resource)


def test_describe_package():
    package = describe(["data/table.csv"])
    assert isinstance(package, Package)


def test_describe_package_pattern():
    package = describe("data/chunk*.csv")
    assert isinstance(package, Package)


def test_describe_package_type_package():
    package = describe(["data/table.csv"], type="package")
    assert isinstance(package, Package)
