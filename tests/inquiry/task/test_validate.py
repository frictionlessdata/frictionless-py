from frictionless import InquiryTask


# General


def test_inquiry_task_validate():
    inquiry = InquiryTask(path="data/table.csv")
    report = inquiry.validate()
    assert report.valid


def test_inquiry_task_validate_strict():
    inquiry = InquiryTask(resource="data/resource.json", strict=True)
    report = inquiry.validate()
    assert not report.valid
