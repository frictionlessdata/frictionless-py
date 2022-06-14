from frictionless import InquiryTask


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
