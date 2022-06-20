from frictionless import Inquiry, InquiryTask


# Inquiry


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


# InquiryTask


def test_inquiry_task_to_descriptor():
    task = InquiryTask(path="data/table.csv")
    assert task.to_descriptor() == {"path": "data/table.csv"}
