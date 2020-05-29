from goodtables import ReportTable, errors


# ReportTable


def test_table_report_valid():
    table = create_report_table(errors=[])
    assert table['valid'] is True
    assert table['errorCount'] == 0
    assert table.flatten(['code']) == []


def test_table_report_invalid():
    table = create_report_table(errors=[errors.SourceError(details='details')])
    assert table['valid'] is False
    assert table['errorCount'] == 1
    assert table.flatten(['code']) == [['source-error']]


# Helpers


def create_report_table(
    *,
    time='time',
    source='source',
    headers=[],
    scheme='scheme',
    format='format',
    encoding='encoding',
    compression='compression',
    schema={},
    dialect={},
    row_count=0,
    errors=[]
):
    return ReportTable(
        time=time,
        source=source,
        headers=headers,
        scheme=scheme,
        format=format,
        encoding=encoding,
        compression=compression,
        schema=schema,
        dialect=dialect,
        row_count=row_count,
        errors=errors,
    )
