# Cell Checks

## ASCII Value

If you want to skip non-ascii characters, this check helps to notify if there are any in data during validation. Here is how we can use this check:

```python title="Python"
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

## Deviated Cell

This check identifies deviated cells from the normal ones. To flag the deviated cell, the check compares the length of the characters in each cell with a threshold value. The threshold value is either 5000 or value calculated using Python's built-in `statistics` module which is average plus(+) three standard deviation. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/main/frictionless/checks/cell/deviated_value.py). For example:

> Download [`issue-1066.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/issue-1066.csv) to reproduce the examples (right-click and "Save link as")..

```python title="Python"
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

## Deviated Value

This check uses Python's built-in `statistics` module to check a field's data for deviations. By default, deviated values are outside of the average +- three standard deviations. Take a look at the [API Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/api-reference/README.md#deviatedvaluecheck) for more details about available options and default values. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/7ae8bae9a9197adbfe443233a6bad8a94e065ece/frictionless/checks/heuristic.py#L94). For example:

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

## Forbidden Value

This check ensures that some field doesn't have any forbidden or denylist values. For example:

```python title="Python"
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

## Sequential Value

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

## Truncated Value

Sometime during data export from a database or other storage, data values can be truncated. This check tries to detect such truncation. Let's explore some truncation indicators:

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
