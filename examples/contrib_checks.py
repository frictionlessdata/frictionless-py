from pprint import pprint
from goodtables import validate


# blacklisted-value

report = validate('data/blacklisted_value.csv', checks=[
    {'blacklisted-value': {'column': 'name', 'blacklist': ['bug', 'bad']}},
])
pprint(report)
pprint('---')


# deviated-value

report = validate('data/deviated_value.csv', checks=[
    {'deviated-value': {'column': 'score', 'interval': [-1, 1], 'average': 'median'}},
])
pprint(report)
pprint('---')


# sequential-value

report = validate('data/sequential_value.csv', checks=[
    {'sequential-value': {'column': 'id'}},
])
pprint(report)
pprint('---')


# truncated-value

report = validate('data/truncated_value.csv', checks=[
    'truncated-value',
])
pprint(report)
pprint('---')


# custom-check

report = validate('data/custom_constraint.csv', checks=[
    {'custom-constraint': {'constraint': 'salary > bonus * 4'}},
])
pprint(report)
pprint('---')
