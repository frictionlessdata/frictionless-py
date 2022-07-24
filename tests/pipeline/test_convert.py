import json
import pytest
from frictionless import Pipeline, steps


# General


def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


def test_pipeline_from_descriptor_tasks_v1x5():
    with pytest.warns(UserWarning):
        descriptor = {"tasks": [{"steps": [{"type": "table-normalize"}]}]}
        pipeline = Pipeline.from_descriptor(descriptor)
        assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


# Yaml


@pytest.mark.xfail(reason="issue-1205")
def test_pipeline_to_yaml():
    pipeline = Pipeline.from_descriptor("data/pipeline.json")
    output_file_path = "data/fixtures/convert/pipeline.yaml"
    with open(output_file_path) as file:
        assert pipeline.to_yaml().strip() == file.read().strip()


# Json


def test_pipeline_to_json():
    pipeline = Pipeline.from_descriptor("data/pipeline.yaml")
    assert json.loads(pipeline.to_json()) == {
        "name": "pipeline",
        "steps": [{"type": "cell-set", "fieldName": "population", "value": 100}],
    }


# Markdown


@pytest.mark.xfail(reason="issue-1205")
def test_pipeline_to_markdown():
    pipeline = Pipeline.from_descriptor("data/pipeline.json")
    output_file_path = "data/fixtures/convert/pipeline.md"
    with open(output_file_path) as file:
        assert pipeline.to_markdown().strip() == file.read()
