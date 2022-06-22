import pytest
from frictionless import Pipeline, steps


# General


@pytest.mark.only
def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    print(pipeline.metadata_properties())
    descriptor = pipeline.to_descriptor()
    assert descriptor == {"steps": [{"code": "table-normalize"}]}
