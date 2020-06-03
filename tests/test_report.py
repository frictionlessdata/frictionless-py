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
    scheme='scheme',
    format='format',
    encoding='encoding',
    compression='compression',
    headers=None,
    headers_row=None,
    headers_joiner=None,
    pick_fields=None,
    skip_fields=None,
    limit_fields=None,
    offset_fields=None,
    pick_rows=None,
    skip_rows=None,
    limit_rows=None,
    offset_rows=None,
    schema=None,
    dialect=None,
    row_count=0,
    errors=[]
):
    return ReportTable(
        time=time,
        source=source,
        scheme=scheme,
        format=format,
        encoding=encoding,
        compression=compression,
        headers=headers,
        headers_row=headers_row,
        headers_joiner=headers_joiner,
        pick_fields=pick_fields,
        skip_fields=skip_fields,
        limit_fields=limit_fields,
        offset_fields=offset_fields,
        pick_rows=pick_rows,
        skip_rows=skip_rows,
        limit_rows=limit_rows,
        offset_rows=offset_rows,
        schema=schema,
        dialect=dialect,
        row_count=row_count,
        errors=errors,
    )
