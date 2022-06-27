from frictionless import validate


def test_report_validate():
    report = validate("data/table.csv")
    assert report.validate().valid
