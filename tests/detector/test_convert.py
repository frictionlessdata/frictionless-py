import json
import yaml
from frictionless import Detector

# Yaml


def test_detector_to_yaml():
    detector = Detector.from_descriptor("data/detector.json")
    expected_file_path = "data/detector.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(detector.to_yaml()) == yaml.safe_load(file.read())


# Json


def test_detector_to_json():
    detector = Detector.from_descriptor("data/detector.yaml")
    assert json.loads(detector.to_json()) == {
        "fieldConfidence": 1,
        "fieldFloatNumbers": True,
        "fieldMissingValues": ["", "67"],
    }
