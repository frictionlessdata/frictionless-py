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

## Reference

```yaml reference
references:
  - frictionless.fields.DateField
```
