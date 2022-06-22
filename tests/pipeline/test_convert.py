from frictionless import Pipeline, steps


# General


def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    descriptor = pipeline.to_descriptor()
    assert descriptor == {"steps": [{"code": "table-normalize"}]}
