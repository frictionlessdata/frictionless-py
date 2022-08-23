# Datetime Field

## Overview

A date with a time (by default in ISO8601 format). Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#datetime).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['2022-08-22T12:00:00']]
rows = extract(data, schema=Schema(fields=[fields.DatetimeField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.DatetimeField
```
