from frictionless import InquiryTask


# General


def test_inquiry_task():
    task = InquiryTask(path="data/table.csv")
    assert task.path == "data/table.csv"


def test_inquiry_task_from_resource_descriptor():
    task = InquiryTask(resource="data/resource.json")
    assert task.resource == "data/resource.json"


def test_inquiry_task_from_package_descriptor():
    task = InquiryTask(package="data/package.json")
    assert task.package == "data/package.json"
