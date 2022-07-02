from frictionless import Pipeline


# General


def test_pipeline_resource():
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"code": "cell-set", "fieldName": "population", "value": 100},
            ],
        }
    )
    report = pipeline.validate()
    assert report.valid
