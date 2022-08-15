from frictionless import InquiryTask, system


# General


def test_inquiry_task_validate():
    inquiry = InquiryTask(path="data/table.csv")
    report = inquiry.validate()
    assert report.valid


def test_inquiry_task_validate_standards_v2_strict():
    inquiry = InquiryTask(resource="data/resource.json")
    with system.use_context(standards="v2-strict"):
        report = inquiry.validate()
    assert not report.valid
