from pprint import pprint
from jsontableschema import Table
from goodtables import Inspector, check

error = {
    'code': 'unicode-found',
    'type': 'structure',
    'context': 'body',
}
@check(error, after='duplicate-row')
def unicode_found(errors, columns, row_number, state=None):
    for column in columns:
        if len(column) == 4:
            if column['value'] == '中国人':
                message = 'Row %s has unicode in column %s' % (row_number, column['number'])
                errors.append({
                    'code': 'unicode-found',
                    'message': message,
                    'row-number': row_number,
                    'column-number': column['number'],
                })


inspector = Inspector(custom_checks=[unicode_found])
report = inspector.inspect('data/valid.csv')
pprint(report)
