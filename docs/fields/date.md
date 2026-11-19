# Date Field

## Overview

A date without a time (by default in ISO8601 format). Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#date).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['2022-08-22']]
rows = extract(data, schema=Schema(fields=[fields.DateField(name='name')]))
print(rows)
```

## Partial dates

The default `date` format expects a complete calendar date such as `2024-05-13`.
With `format: any`, a partial date such as `2024-05` can be filled in using the
current day. The parsed date can therefore change depending on when you read the
same data.

Use a [year](year.md) field for `YYYY` values or a [yearmonth](yearmonth.md) field
for `YYYY-MM` values. If a column mixes years, year-months, and full dates, use a
[string](string.md) field to preserve the original values.

```python script tabs=Python
from frictionless import Resource, Schema, fields

data = [
    ["year", "year_month", "as_recorded"],
    ["2024", "2024-05", "2024"],
    ["2024", "2024-05", "2024-05"],
    ["2024", "2024-05", "2024-05-13"],
]
schema = Schema(fields=[
    fields.YearField(name="year"),
    fields.YearmonthField(name="year_month"),
    fields.StringField(name="as_recorded"),
])
rows = Resource(data=data, schema=schema).read_rows()

assert rows[0]["year"] == 2024
assert tuple(rows[0]["year_month"]) == (2024, 5)
assert [row["as_recorded"] for row in rows] == ["2024", "2024-05", "2024-05-13"]
print([row.to_list() for row in rows])
```

## Reference

```yaml reference
references:
  - frictionless.fields.DateField
```
