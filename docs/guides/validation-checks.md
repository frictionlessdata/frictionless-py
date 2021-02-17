---
title: Validation Checks
---

There are various validation checks included in the core Frictionless Framework along with an ability to create custom checks. Let's review what's in the box.

## Baseline Check

The Baseline Check is always enabled. It makes various small checks revealing a great deal of tabular errors. There is a `report.tables[].scope` property to check what exact errors it have been checked for:

```python title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv')
pprint(report.table.scope)
```
```
['dialect-error',
 'schema-error',
 'field-error',
 'extra-header',
 'missing-header',
 'blank-header',
 'duplicate-header',
 'non-matching-header',
 'extra-cell',
 'missing-cell',
 'blank-row',
 'type-error',
 'constraint-error',
 'unique-error',
 'primary-key-error',
 'foreign-key-error',
 'checksum-error']
```

## Heuristic Checks

There is a group of checks that indicate probable errors. You need to use the `checks` argument of the `validate` function to activate one or more of these checks.

### Duplicate Row

This check is self-explanatory. You need to take into account that checking for duplicate rows can lean to high memory consumption on big files. Here is an example:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = 'header\nvalue\nvalue'
report = validate(source, scheme='text', format='csv', checks=[checks.duplicate_row()])
pprint(report.flatten(['code', 'message']))
```
```
[['duplicate-row',
  'Row at position 3 is duplicated: the same as row at position "2"']]
```

### Deviated Value

This check uses the Python's builtin `statistics` module to check a field's data for deviations. By default, deviated values are outside of the average +- three standard deviations. Take a look at the [API Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/api-reference/README.md#deviatedvaluecheck) for more details about available options and default values. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/7ae8bae9a9197adbfe443233a6bad8a94e065ece/frictionless/checks/heuristic.py#L94). For example:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [["temperature"], [1], [-2], [7], [0], [1], [2], [5], [-4], [1000], [8], [3]]
report = validate(source, checks=[checks.deviated_value(field_name="temperature")])
pprint(report.flatten(["code", "message"]))

```
```
[['deviated-value',
  'There is a possible error because the value is deviated: value "1000" in '
  'row at position "10" and field "temperature" is deviated "[-809.88, '
  '995.52]"']]
```

### Truncated Value

Sometime during the export from a database or another storage, data values can be truncated. This check tries to detect it. Let's explore some truncation indicators:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [["int", "str"], ["a" * 255, 32767], ["good", 2147483647]]
report = validate(source, checks=[checks.truncated_value()])
pprint(report.flatten(["code", "message"]))
```
```
[['truncated-value',
  'The cell '
  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa '
  'in row at position 2 and field int at position 1 has an error: value  is '
  'probably truncated'],
 ['truncated-value',
  'The cell 32767 in row at position 2 and field str at position 2 has an '
  'error: value  is probably truncated'],
 ['truncated-value',
  'The cell 2147483647 in row at position 3 and field str at position 2 has an '
  'error: value  is probably truncated']]
```

## Regulation Checks

In the contrary to heuristic checks, regulation checks gives you an ability to provide additional rules for your data. Use the `checks` argument of the `validate` function to active one or more of these checks.

### Forbidden Value

This check ensures that some field doesn't have any blacklisted values. For example:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = b'header\nvalue1\nvalue2'
checks = [checks.forbidden_values(field_name='header', values=['value2'])]
report = validate(source, format='csv', checks=checks)
pprint(report.flatten(['code', 'message']))
```
```
[['blacklisted-value',
  'The cell value2 in row at position 3 and field header at position 1 has an '
  'error: blacklisted values are "[\'value2\']"']]
```

### Sequential Value

This check gives us an opportunity to validate sequential fields like primary keys or other similar data. It doesn't need to start from 0 or 1. We're providing a field name:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = b'header\n2\n3\n5'
report = validate(source, format='csv', checks=[checks.sequential_value(field_name='header')])
pprint(report.flatten(['code', 'message']))
```
```
[['sequential-value',
  'The cell 5 in row at position 4 and field header at position 1 has an '
  'error: the value is not sequential']]
```

### Row Constraint

This checks is the most powerful one as it uses the external `simpleeval` package allowing to evaluate arbitrary python expressions on data rows. Let's show on an example:

```python title="Python"
from pprint import pprint
from frictionless import validate

source = [
  ["row", "salary", "bonus"],
  [2, 1000, 200],
  [3, 2500, 500],
  [4, 1300, 500],
  [5, 5000, 1000],
]
report = validate(source, checks=checks.row_constraint(constraint="salary == bonus * 5"))
pprint(report.flatten(["code", "message"]))
```
```
[['row-constraint',
  'The row at position 4 has an error: the row constraint to conform is '
  '"salary == bonus * 5"']]
```

## Custom Checks

There are many cases when built-in Frictionless' checks are not enough. It can be a business logic rule or specific quality requirement to the data. With Frictionless it's very easy to use your own custom checks. Let's see on an example:

```python title="Python"
from pprint import pprint
from frictionless import validate, errors, Check

# Create check
def forbidden_two(row):
    if row['header'] == 2:
      note = f"number {self['number']} is forbidden!"
      yield errors.CellError.from_row(row, note=note, field_name='header')

# Validate table
source = b'header\n1\n2\n3'
report = validate(source,  format='csv', checks=[forbidden_two])
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
```
```
[[3, 1, 'cell-error', 'number 2 is forbidden!']]
```

Usually, it also makes sense to create a custom error for your custom check. The Check class provides other useful methods like `validate_header` etc. Please read "API Reference" to learn it in details.

Learn more about custom checks in the [Check Guide](check-guide.md).
