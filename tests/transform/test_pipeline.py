from frictionless import transform


# General


def test_transform_pipeline():
    source = {
        "type": "resource",
        "source": {"path": "data/transform.csv"},
        "steps": [
            {"type": "cellSet", "spec": {"fieldName": "population", "value": 100}},
        ],
    }
    target = transform(source)
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
