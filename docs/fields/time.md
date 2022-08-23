# Time Field

## Overview

A time without a date. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#time).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['15:00:00']]
rows = extract(data, schema=Schema(fields=[fields.TimeField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.TimeField
```
