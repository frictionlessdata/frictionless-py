from goodtables import TableReport, errors


# TableReport


def test_table_report_valid():
    report = TableReport(errors=[])
    assert report['valid'] == True
    assert report['errorCount'] == 0
    assert report.flatten(['code']) == []


def test_table_report_invalid():
    report = TableReport(errors=[errors.LoadingError(details='details')])
    assert report['valid'] == False
    assert report['errorCount'] == 1
    assert report.flatten(['code']) == [['loading-error']]
