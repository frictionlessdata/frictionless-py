import json
import yaml
from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()], pick_errors=["type-error"])
    descriptor = checklist.to_descriptor()
    print(descriptor)
    assert descriptor == {
        "checks": [{"type": "ascii-value"}],
        "pickErrors": ["type-error"],
    }


# Yaml


def test_checklist_to_yaml():
    checklist = Checklist.from_descriptor("data/checklist.json")
    expected_file_path = "data/checklist.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(checklist.to_yaml()) == yaml.safe_load(file.read())


# Json


def test_checklist_to_json():
    checklist = Checklist.from_descriptor("data/checklist.yaml")
    assert json.loads(checklist.to_json()) == {
        "checks": [
            {
                "type": "deviated-cell",
                "interval": 3,
                "ignoreFields": ["Latitudine", "Longitudine"],
            },
            {"type": "ascii-value"},
        ]
    }
