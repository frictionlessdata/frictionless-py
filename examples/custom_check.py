from pprint import pprint
from goodtables import Inspector, check

@check('unicode-found', type='structure', context='body', after='duplicate-row')
def unicode_found(errors, columns, row_number, state=None):
    for column in columns:
        if len(column) == 4:
            if column['value'] == '中国人':
                message = 'Row {row_number} has unicode in column {column_number}'
                message = message.format(
                    row_number=row_number,
                    column_number=column['number'])
                errors.append({
                    'code': 'unicode-found',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })


inspector = Inspector(custom_checks=[unicode_found])
report = inspector.inspect('data/valid.csv')
pprint(report)
