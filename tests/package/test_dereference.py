import pytest
from frictionless import Package


# General


@pytest.mark.xfail(reason="dereference")
def test_package_dereference():
    # TODO: we need to support opening dir as a package using datapackage.yaml
    package = Package("data/dereference/package")
    package.get_resource("resource1").name = "resource1"
    package.get_resource("resource2").name = "resource2"
    assert package.to_descriptor() == {
        "name": "package",
        "resources": ["resource1.yaml", "resource2.yaml"],
    }
