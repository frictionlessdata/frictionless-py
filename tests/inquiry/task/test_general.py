from frictionless import InquiryTask


def test_inquiry_task():
    task = InquiryTask(path="data/table.csv")
    assert task.path == "data/table.csv"
