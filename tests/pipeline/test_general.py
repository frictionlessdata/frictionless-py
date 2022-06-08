from frictionless import Pipeline, steps


# General


def test_pipeline():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.step_codes == ["table-normalize"]
    assert pipeline.limit_memory == 1000
    assert pipeline.allow_parallel is False


def test_pipeline_from_descriptor():
    pipeline = Pipeline(
        {
            "steps": [{"code": "table-normalize"}],
            "limitMemory": 100,
            "allowParallel": True,
        }
    )
    assert pipeline.step_codes == ["table-normalize"]
    assert pipeline.limit_memory == 100
    assert pipeline.allow_parallel is True
    assert isinstance(pipeline.steps[0], steps.table_normalize)
