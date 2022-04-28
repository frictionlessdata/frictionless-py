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


# Issues


def test_inquiry_pprint_1029():
    inquiry = Inquiry(
        {
            "tasks": [
                {"source": "data/capital-valid.csv"},
                {"source": "data/capital-invalid.csv"},
            ]
        }
    )
    expected = """{'tasks': [{'source': 'data/capital-valid.csv'},
           {'source': 'data/capital-invalid.csv'}]}"""
    assert repr(inquiry) == expected
