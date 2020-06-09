from goodtables import validate, ReportTable, errors


# Report


def test_validate_report_props():
    report = validate('data/table.csv')
    assert report.time
    assert report.valid is True
    assert report.version.startswith('3')
    assert report.table_count == 1
    assert report.error_count == 0
    assert report.table.time
    assert report.table.valid is True
    assert report.table.scope == [
        'extra-header',
        'missing-header',
        'blank-header',
        'duplicate-header',
        'non-matching-header',
        'extra-cell',
        'missing-cell',
        'blank-row',
        'required-error',
        'type-error',
        'constraint-error',
        'size-error',
        'hash-error',
        'unique-error',
        'primary-key-error',
        'foreign-key-error',
    ]
    assert report.table.row_count == 2
    assert report.table.error_count == 0
    assert report.table['source'] == 'data/table.csv'
    assert report.table['headers'] == ['id', 'name']
    assert report.table['scheme'] == 'file'
    assert report.table['format'] == 'csv'
    assert report.table['encoding'] == 'utf-8'
    assert report.table['dialect'] == {}
    assert report.table['errors'] == []
    assert report.table['schema'] == {
        'fields': [
            {'format': 'default', 'name': 'id', 'type': 'integer'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
        ],
        'missingValues': [''],
    }


# ReportTable


def test_table_report_valid():
    table = create_report_table(errors=[])
    assert table.valid is True
    assert table.error_count == 0
    assert table.flatten(['code']) == []


def test_table_report_invalid():
    table = create_report_table(errors=[errors.SourceError(details='details')])
    assert table.valid is False
    assert table.error_count == 1
    assert table.flatten(['code']) == [['source-error']]


# Helpers


def create_report_table(
    *,
    time='time',
    scope=[],
    row_count=0,
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
    errors=[]
):
    return ReportTable(
        time=time,
        scope=scope,
        row_count=row_count,
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
        errors=errors,
    )
