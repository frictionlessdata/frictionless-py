---
script:
  basepath: data
topics:
  selector: h2
---

# Cell Checks

## ASCII Value

If you want to skip non-ascii characters, this check helps to notify if there are any in data during validation. Here is how we can use this check.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source=[["s.no","code"],[1,"ssµ"]]
report = validate(source, checks=[checks.ascii_value()])
pprint(report.flatten(["type", "message"]))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.ascii_value
```

## Deviated Cell

This check identifies deviated cells from the normal ones. To flag the deviated cell, the check compares the length of the characters in each cell with a threshold value. The threshold value is either 5000 or value calculated using Python's built-in `statistics` module which is average plus(+) three standard deviation. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/main/frictionless/checks/cell/deviated_value.py). For example:

### Example

> Download [`issue-1066.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/issue-1066.csv) to reproduce the examples (right-click and "Save link as")..

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

report = validate("issue-1066.csv", checks=[checks.deviated_cell()])
pprint(report.flatten(["type", "message"]))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.deviated_cell
```

## Deviated Value

This check uses Python's built-in `statistics` module to check a field's data for deviations. By default, deviated values are outside of the average +- three standard deviations. Take a look at the [API Reference](../../docs/checks/cell.html#reference-checks.deviated_value) for more details about available options and default values. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/7ae8bae9a9197adbfe443233a6bad8a94e065ece/frictionless/checks/heuristic.py#L94). For example:

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = [["temperature"], [1], [-2], [7], [0], [1], [2], [5], [-4], [1000], [8], [3]]
report = validate(source, checks=[checks.deviated_value(field_name="temperature")])
pprint(report.flatten(["type", "message"]))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.deviated_value
```

## Forbidden Value

This check ensures that some field doesn't have any forbidden or denylist values.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = b'header\nvalue1\nvalue2'
checks = [checks.forbidden_value(field_name='header', values=['value2'])]
report = validate(source, format='csv', checks=checks)
pprint(report.flatten(['type', 'message']))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.forbidden_value
```

## Sequential Value

This check gives us an opportunity to validate sequential fields like primary keys or other similar data. It doesn't need to start from 0 or 1. We're providing a field name.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = b'header\n2\n3\n5'
report = validate(source, format='csv', checks=[checks.sequential_value(field_name='header')])
pprint(report.flatten(['type', 'message']))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.sequential_value
```

## Truncated Value

Sometime during data export from a database or other storage, data values can be truncated. This check tries to detect such truncation. Let's explore some truncation indicators.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = [["int", "str"], ["a" * 255, 32767], ["good", 2147483647]]
report = validate(source, checks=[checks.truncated_value()])
pprint(report.flatten(["type", "message"]))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.truncated_value
```
