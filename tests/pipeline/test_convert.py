import json
import pytest
import yaml
from frictionless import Pipeline, steps


# General


def test_pipeline_to_descriptor():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


def test_pipeline_from_descriptor_tasks_framework_v4():
    with pytest.warns(UserWarning):
        descriptor = {"tasks": [{"steps": [{"type": "table-normalize"}]}]}
        pipeline = Pipeline.from_descriptor(descriptor)
        assert pipeline.to_descriptor() == {"steps": [{"type": "table-normalize"}]}


# Yaml


def test_pipeline_to_yaml():
    pipeline = Pipeline.from_descriptor("data/pipeline.json")
    expected_file_path = "data/pipeline.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(pipeline.to_yaml()) == yaml.safe_load(file.read())


# Json


def test_pipeline_to_json():
    pipeline = Pipeline.from_descriptor("data/pipeline.yaml")
    assert json.loads(pipeline.to_json()) == {
        "name": "pipeline",
        "steps": [{"type": "cell-set", "fieldName": "population", "value": 100}],
    }
