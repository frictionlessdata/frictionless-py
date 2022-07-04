from frictionless import Resource


# General


def test_report_validate():
    resource = Resource("data/table.csv")
    report = resource.validate()
    report = report.validate()
    assert report.valid
