import pytest

from frictionless import Catalog, Dataset, Package, platform

# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_catalog_infer():
    dataset = Dataset(name="name", package=Package("data/infer/*.csv"))
    catalog = Catalog(datasets=[dataset])
    assert catalog.to_descriptor() == {
        "datasets": [
            {
                "name": "name",
                "package": {
                    "resources": [
                        {
                            "name": "data",
                            "type": "table",
                            "path": "data/infer/data.csv",
                            "scheme": "file",
                            "format": "csv",
                            "mediatype": "text/csv",
                        },
                        {
                            "name": "data2",
                            "type": "table",
                            "path": "data/infer/data2.csv",
                            "scheme": "file",
                            "format": "csv",
                            "mediatype": "text/csv",
                        },
                    ],
                },
            }
        ]
    }
