import json
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
    output_file_path = "data/fixtures/convert/inquiry.yaml"
    with open(output_file_path) as file:
        assert inquiry.to_yaml().strip() == file.read().strip()


# Json


def test_inquiry_to_json():
    inquiry = Inquiry.from_descriptor("data/inquiry.yaml")
    assert json.loads(inquiry.to_json()) == {
        "tasks": [
            {"resource": "data/capital-valid.csv"},
            {"resource": "data/capital-invalid.csv"},
        ]
    }


# Markdown


def test_inquiry_to_markdown():
    inquiry = Inquiry.from_descriptor("data/inquiry.json")
    output_file_path = "data/fixtures/convert/inquiry.md"
    with open(output_file_path) as file:
        assert inquiry.to_markdown().strip() == file.read()
