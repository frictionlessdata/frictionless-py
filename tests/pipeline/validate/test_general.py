from frictionless import Pipeline


def test_pipeline_resource():
    pipeline = Pipeline(
        {
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
    )
    report = pipeline.validate()
    assert report.valid
