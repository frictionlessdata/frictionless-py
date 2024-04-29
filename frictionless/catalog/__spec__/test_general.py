from frictionless import Catalog, Dataset

# General


def test_catalog():
    dataset = Dataset(name="name", package="data/package.json")
    catalog = Catalog(datasets=[dataset])
    print(catalog)
    assert catalog.dataset_names == ["name"]
    assert catalog.to_descriptor() == {
        "datasets": [{"name": "name", "package": "data/package.json"}]
    }
