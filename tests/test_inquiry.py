from frictionless import Inquiry, InquiryTask


# General


def test_inquiry():
    inquiry = Inquiry(tasks=[{"source": "data/table.csv"}, {"source": "data/matrix.csv"}])
    report = inquiry.run()
    assert report.valid


def test_inquiry_with_task_class():
    inquiry = Inquiry(
        tasks=[
            InquiryTask(source="data/table.csv"),
            InquiryTask(source="data/matrix.csv"),
        ]
    )
    report = inquiry.run()
    assert report.valid
