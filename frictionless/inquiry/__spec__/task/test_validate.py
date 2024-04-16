import pytest

from frictionless import InquiryTask, system

# General


def test_inquiry_task_validate():
    inquiry = InquiryTask(path="data/table.csv")
    report = inquiry.validate()
    assert report.valid


@pytest.mark.skip
def test_inquiry_task_validate_standards_v2():
    inquiry = InquiryTask(resource="data/resource.json")
    with system.use_context(standards="v2"):
        report = inquiry.validate()
    assert not report.valid
