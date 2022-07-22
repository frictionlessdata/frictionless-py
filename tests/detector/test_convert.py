import json
from frictionless import Detector

# Yaml


def test_detector_to_yaml():
    detector = Detector.from_descriptor("data/detector.json")
    output_file_path = "data/fixtures/convert/detector.yaml"
    with open(output_file_path) as file:
        assert detector.to_yaml().strip() == file.read().strip()


# Json


def test_detector_to_json():
    detector = Detector.from_descriptor("data/detector.yaml")
    assert json.loads(detector.to_json()) == {
        "fieldConfidence": 1,
        "fieldFloatNumbers": True,
        "fieldMissingValues": ["", "67"],
    }


# Markdown


def test_detector_to_markdown():
    detector = Detector.from_descriptor("data/detector.json")
    output_file_path = "data/fixtures/convert/detector.md"
    with open(output_file_path) as file:
        assert detector.to_markdown().strip() == file.read()
