# Table Checks

## Table Dimensions

This check is used to validate if your data has expected dimensions as: exact number of rows (`num_rows`), minimum (`min_rows`) and maximum (`max_rows`) number of rows, exact number of fields (`num_fields`), minimum (`min_fields`) and maximum (`max_fields`) number of fields.

```python title="Python"
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

```python title="Python"
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

```python title="Python"
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
