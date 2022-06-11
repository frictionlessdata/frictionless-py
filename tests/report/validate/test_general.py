from frictionless import validate


def test_report_validate():
    report = validate("data/table.csv")
    print(report.validate())
    assert report.validate().valid
