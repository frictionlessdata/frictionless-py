from frictionless import Resource


# General


def test_report_validate():
    resource = Resource("data/table.csv")
    report = resource.validate()
    assert report.to_descriptor()
