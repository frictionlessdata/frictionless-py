from frictionless import Pipeline


# General


def test_pipeline_resource():
    report = Pipeline.validate_descriptor(
        {
            "steps": [
                {"type": "cell-set", "fieldName": "population", "value": 100},
            ],
        }
    )
    assert report.valid
