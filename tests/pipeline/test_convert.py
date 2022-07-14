import pytest
from frictionless import Pipeline, steps


# General


def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


def test_pipeline_from_descriptor_tasks_v1x5():
    with pytest.warns(UserWarning):
        descriptor = {"tasks": [{"steps": [{"code": "table-normalize"}]}]}
        pipeline = Pipeline.from_descriptor(descriptor)
        assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}
