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
