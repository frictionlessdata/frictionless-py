from frictionless import Package


# General


def test_package_dereference():
    package = Package("data/dereference/package/datapackage.yaml")
    package.get_resource("resource1").name = "resource1"
    package.get_resource("resource2").name = "resource2"
    assert package.to_descriptor() == {
        "name": "package",
        "resources": ["resource1.yaml", "resource2.yaml"],
    }


def test_package_dereference_from_dir_with_datapackage():
    package = Package("data/dereference/package")
    package.get_resource("resource1").name = "resource1"
    package.get_resource("resource2").name = "resource2"
    assert package.to_descriptor() == {
        "name": "package",
        "resources": ["resource1.yaml", "resource2.yaml"],
    }
