import pytest
from frictionless import Inquiry, InquiryTask


# Inquiry


def test_inquiry():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/table.csv"},
                {"path": "data/matrix.csv"},
            ]
        }
    )
    report = inquiry.validate()
    assert report.valid


def test_inquiry_with_task_class():
    inquiry = Inquiry(
        tasks=[
            InquiryTask(path="data/table.csv"),
            InquiryTask(path="data/matrix.csv"),
        ]
    )
    report = inquiry.validate()
    assert report.valid


@pytest.mark.skip
def test_inquiry_pprint_1029():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/capital-valid.csv"},
                {"path": "data/capital-invalid.csv"},
            ]
        }
    )
    expected = """{'tasks': [{'path': 'data/capital-valid.csv'},
           {'path': 'data/capital-invalid.csv'}]}"""
    assert repr(inquiry) == expected


# InquiryTask


def test_inquiry_task():
    task = InquiryTask(path="data/table.csv")
    assert task.type == "resource"
    assert task.path == "data/table.csv"


def test_inquiry_task_from_resource_descriptor():
    task = InquiryTask(descriptor="data/resource.json")
    assert task.descriptor == "data/resource.json"
    assert task.type == "resource"


def test_inquiry_task_from_package_descriptor():
    task = InquiryTask(descriptor="data/package.json")
    assert task.descriptor == "data/package.json"
    assert task.type == "package"
