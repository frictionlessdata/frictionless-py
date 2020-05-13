from goodtables import ReportTable, errors


# ReportTable


def test_table_report_valid():
    table = ReportTable(errors=[])
    assert table['valid'] is True
    assert table['errorCount'] == 0
    assert table.flatten(['code']) == []


def test_table_report_invalid():
    table = ReportTable(errors=[errors.LoadingError(details='details')])
    assert table['valid'] is False
    assert table['errorCount'] == 1
    assert table.flatten(['code']) == [['loading-error']]
