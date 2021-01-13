from frictionless import Pipeline


# General


def test_pipeline_resource():
    pipeline = Pipeline(
        {
            "type": "resource",
            "source": {"path": "data/transform.csv"},
            "steps": [
                {"step": "cell-set", "fieldName": "population", "value": 100},
            ],
        }
    )
    target = pipeline.run()
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


def test_pipeline_package():
    pipeline = Pipeline(
        {
            "type": "package",
            "source": "data/package/datapackage.json",
            "steps": [
                {"step": "resource-remove", "name": "data2"},
            ],
        }
    )
    target = pipeline.run()
    assert target.resource_names == ["data"]
