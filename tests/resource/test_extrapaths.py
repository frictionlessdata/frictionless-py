from frictionless import Resource


# General


def test_resource_extrapaths():
    resource = Resource(
        path="data/tables/chunk1.csv",
        extrapaths=["data/tables/chunk2.csv"],
    )
    assert resource.place == "data/tables/chunk1.csv (multipart)"


def test_resource_extrapaths_basepath():
    resource = Resource(
        path="chunk1.csv",
        extrapaths=["chunk2.csv"],
        basepath="data/tables",
    )
    assert resource.place == "chunk1.csv (multipart)"
