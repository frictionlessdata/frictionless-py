import textwrap
from frictionless import Inquiry, InquiryTask


# General


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


def test_inquiry_pprint():
    inquiry = Inquiry.from_descriptor(
        {
            "tasks": [
                {"path": "data/capital-valid.csv"},
                {"path": "data/capital-invalid.csv"},
            ]
        }
    )
    expected = """
    {'tasks': [{'path': 'data/capital-valid.csv'},
               {'path': 'data/capital-invalid.csv'}]}"""
    assert repr(inquiry) == textwrap.dedent(expected).strip()


def test_inquiry_name():
    inquiry = Inquiry(name="name", tasks=[InquiryTask(path="data/table.csv")])
    report = inquiry.validate()
    assert report.valid
    assert report.name == "name"
