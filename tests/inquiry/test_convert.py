import json
import yaml
from frictionless import Inquiry, InquiryTask


# General


def test_inquiry_to_descriptor():
    inquiry = Inquiry(
        tasks=[
            InquiryTask(path="data/table.csv"),
            InquiryTask(path="data/matrix.csv"),
        ]
    )
    assert inquiry.to_descriptor() == {
        "tasks": [
            {"path": "data/table.csv"},
            {"path": "data/matrix.csv"},
        ]
    }


# Yaml


def test_inquiry_to_yaml():
    inquiry = Inquiry.from_descriptor("data/inquiry.json")
    expected_file_path = "data/inquiry.yaml"

    # Read
    with open(expected_file_path) as file:
        assert yaml.safe_load(inquiry.to_yaml()) == yaml.safe_load(file.read())


# Json


def test_inquiry_to_json():
    inquiry = Inquiry.from_descriptor("data/inquiry.yaml")
    assert json.loads(inquiry.to_json()) == {
        "tasks": [
            {"path": "data/capital-valid.csv"},
            {"path": "data/capital-invalid.csv"},
        ]
    }
