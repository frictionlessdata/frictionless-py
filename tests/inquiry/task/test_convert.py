import pytest
from frictionless import InquiryTask


# General


def test_inquiry_task_to_descriptor():
    task = InquiryTask(path="data/table.csv")
    assert task.to_descriptor() == {"path": "data/table.csv"}


def test_inquiry_task_from_descriptor_legacy_source_framework_v4():
    with pytest.warns(UserWarning):
        task = InquiryTask.from_descriptor({"source": "metadata.json"})
        assert task.to_descriptor() == {"resource": "metadata.json"}


def test_inquiry_task_from_descriptor_legacy_source_with_type_framework_v4():
    with pytest.warns(UserWarning):
        task = InquiryTask.from_descriptor({"source": "metadata.json", "type": "package"})
        assert task.to_descriptor() == {"package": "metadata.json"}
