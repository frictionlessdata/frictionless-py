from pprint import pprint
from goodtables import validate

report = validate('data/sequential_column.csv', checks={
    'sequential-column': {'column': 'id'},
})
pprint(report)
