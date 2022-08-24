---
title: Validation Checks
prepare:
  - cp data/capital-invalid.csv capital-invalid.csv
  - cp data/issue-1066.csv issue-1066.csv
cleanup:
  - rm capital-invalid.csv
  - rm issue-1066.csv
---

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

There are various validation checks included in the core Frictionless Framework along with an ability to create custom checks. Let's review what's in the box.

## Baseline Check

The Baseline Check is always enabled. It makes various small checks that reveal a great deal of tabular errors. There is a `report.tasks[].scope` property to check which exact errors have been checked for:

> Download [`capital-invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-invalid.csv) to reproduce the examples (right-click and "Save link as")..

```python script title="Python"
from pprint import pprint
from frictionless import validate

report = validate('capital-invalid.csv')
pprint(report.task.scope)
```
```
['hash-count-error',
 'byte-count-error',
 'field-count-error',
 'row-count-error',
 'blank-header',
 'extra-label',
 'missing-label',
 'blank-label',
 'duplicate-label',
 'incorrect-label',
 'blank-row',
 'primary-key-error',
 'foreign-key-error',
 'extra-cell',
 'missing-cell',
 'type-error',
 'constraint-error',
 'unique-error']
```

The Baseline Check is incorporated into base Frictionless classes as though Resource, Header, and Row. There is no exact order in which those errors are revealed as it's highly optimized. One should consider the Baseline Check as one unit of validation.

## Heuristic Checks

There is a group of checks that indicate probable errors. You need to use the `checks` argument of the `validate` function to activate one or more of these checks.

### Duplicate Row

This checks for duplicate rows. You need to take into account that checking for duplicate rows can lead to high memory consumption on big files. Here is an example:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = b"header\nvalue\nvalue"
report = validate(source, format="csv", checks=[checks.duplicate_row()])
pprint(report.flatten(["code", "message"]))
```
```
[['duplicate-row',
  'Row at position 3 is duplicated: the same as row at position "2"']]
```

### ASCII Value

If you want to skip non-ascii characters, this check helps to notify if there are any in data during validation. Here is how we can use this check:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source=[["s.no","code"],[1,"ssµ"]]
report = validate(
        source,
        checks=[checks.ascii_value()],
    )
print(report.flatten(["code", "message"]))
```
```
[['non-ascii', 'The cell ssµ in row at position 2 and field code at position 2 has an error: the cell contains non-ascii characters']]
```

### Deviated Cell

This check identifies deviated cells from the normal ones. To flag the deviated cell, the check compares the length of the characters in each cell with a threshold value. The threshold value is either 5000 or value calculated using Python's built-in `statistics` module which is average plus(+) three standard deviation. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/main/frictionless/checks/cell/deviated_value.py). For example:

> Download [`issue-1066.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/issue-1066.csv) to reproduce the examples (right-click and "Save link as")..

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

report = validate(
        "data/issue-1066.csv",
        checks=[
            checks.deviated_cell(
                ignore_fields=[
                    "Latitudine",
                    "Longitudine",
                ]
            )
        ],
    )
pprint(report.flatten(["code", "message"]))
```
```
[['deviated-cell', 'cell at row "35" and field "Gestore" has deviated size']]
```

### Deviated Value

This check uses Python's built-in `statistics` module to check a field's data for deviations. By default, deviated values are outside of the average +- three standard deviations. Take a look at the [API Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/api-reference/README.md#deviatedvaluecheck) for more details about available options and default values. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/7ae8bae9a9197adbfe443233a6bad8a94e065ece/frictionless/checks/heuristic.py#L94). For example:

```python script title="Python"
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

Sometime during data export from a database or other storage, data values can be truncated. This check tries to detect such truncation. Let's explore some truncation indicators:

```python script title="Python"
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

Contrary to heuristic checks, regulation checks give you the ability to provide additional rules for your data. Use the `checks` argument of the `validate` function to active one or more of these checks.

### Forbidden Value

This check ensures that some field doesn't have any forbidden or denylist values. For example:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = b'header\nvalue1\nvalue2'
checks = [checks.forbidden_value(field_name='header', values=['value2'])]
report = validate(source, format='csv', checks=checks)
pprint(report.flatten(['code', 'message']))
```
```
[['forbidden-value',
  'The cell value2 in row at position 3 and field header at position 1 has an '
  'error: forbiddened values are "[\'value2\']"']]
```

### Sequential Value

This check gives us an opportunity to validate sequential fields like primary keys or other similar data. It doesn't need to start from 0 or 1. We're providing a field name:

```python script title="Python"
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

This check is the most powerful one as it uses the external `simpleeval` package allowing you to evaluate arbitrary Python expressions on data rows. Let's show on an example:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.row_constraint(formula="salary == bonus * 5")])
pprint(report.flatten(["code", "message"]))
```
```
[['row-constraint',
  'The row at position 4 has an error: the row constraint to conform is '
  '"salary == bonus * 5"']]
```

### Table Dimensions 

This check is used to validate if your data has expected dimensions as: exact number of rows (`num_rows`), minimum (`min_rows`) and maximum (`max_rows`) number of rows, exact number of fields (`num_fields`), minimum (`min_fields`) and maximum (`max_fields`) number of fields.

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.table_dimensions(num_rows=5)])
pprint(report.flatten(["code", "message"]))
```
```
[['table-dimensions-error',
  'The data source does not have the required dimensions: Current number of '
  'rows is 4, the required is 5']]
```

You can also give multiples limits at the same time:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.table_dimensions(num_rows=5, num_fields=4)])
pprint(report.flatten(["code", "message"]))
```
```
[['table-dimensions-error',
  'The data source does not have the required dimensions: Current number of '
  'fields is 3, the required number is 4'],

[['table-dimensions-error',
  'The data source does not have the required dimensions: Current number of '
  'rows is 4, the required is 5']]
```

It is possible to use de check declaratively as:

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]

report = validate(source, checks=[{"code": "table-dimensions", "minFields": 4, "maxRows": 3}])
pprint(report.flatten(["code", "message"]))
```
```
[['table-dimensions-error',
  'The data source does not have the required dimensions: Current number of '
  'fields is 3, the minimum is 4'],
 ['table-dimensions-error',
  'The data source does not have the required dimensions: Current number of '
  'rows is 4, the maximum is 3']]
```

But the table dimensions check arguments `num_rows`, `min_rows`, `max_rows`, `num_fields`, `min_fields`, `max_fields` must be passed in camelCase format as the example above i.e. `numRows`, `minRows`, `maxRows`, `numFields`, `minFields` and `maxFields`.
