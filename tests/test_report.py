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
    headers=None,
    scheme='scheme',
    format='format',
    encoding='encoding',
    compression='compression',
    pick_fields=None,
    skip_fields=None,
    field_limit=None,
    pick_rows=None,
    skip_rows=None,
    row_limit=None,
    schema=None,
    dialect=None,
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
        pick_fields=pick_fields,
        skip_fields=skip_fields,
        field_limit=field_limit,
        pick_rows=pick_rows,
        skip_rows=skip_rows,
        row_limit=row_limit,
        schema=schema,
        dialect=dialect,
        row_count=row_count,
        errors=errors,
    )
