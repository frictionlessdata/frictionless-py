from frictionless import InquiryTask


# General


def test_inquiry_task():
    task = InquiryTask(path="data/table.csv")
    assert task.to_descriptor() == {"path": "data/table.csv"}
