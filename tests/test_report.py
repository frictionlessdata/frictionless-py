from goodtables import TableReport, errors


# TableReport


def test_table_report():
    report = TableReport(errors=[errors.LoadingError(details='details')])
    assert report.flatten(['code']) == [['loading-error']]
