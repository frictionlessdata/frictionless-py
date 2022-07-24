import pytest
from frictionless import Catalog


# General


@pytest.mark.xfail(reason="dereference")
def test_catalog_dereference():
    # TODO: we need to support opening dir as a catalog using datacatalog.yaml
    catalog = Catalog("data/dereference/catalog")
    catalog.get_package("package1").name = "package1"
    catalog.get_package("package2").name = "package2"
    assert catalog.to_descriptor() == {
        "name": "catalog",
        "packages": ["package1.yaml", "package2.yaml"],
    }
