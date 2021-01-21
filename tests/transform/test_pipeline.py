from frictionless import transform


# General


def test_transform_pipeline():
    pipeline = {
        "tasks": [
            {
                "type": "resource",
                "source": {"path": "data/transform.csv"},
                "steps": [
                    {"code": "cell-set", "fieldName": "population", "value": 100},
                ],
            }
        ]
    }
    status = transform(pipeline)
    assert status.valid
    assert status.task.valid
    assert status.task.target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert status.task.target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
