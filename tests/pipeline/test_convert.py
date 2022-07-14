from frictionless import Pipeline, steps


# General


def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


def test_pipeline_from_descriptor_tasks_v1x5():
    pipeline = Pipeline.from_descriptor(
        {"tasks": [{"steps": [{"code": "table-normalize"}]}]}
    )
    assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}
