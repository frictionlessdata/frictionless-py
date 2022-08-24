# Object Field

## Overview

The field contains data which is valid JSON. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#object).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['{"key": "value"}']]
rows = extract(data, schema=Schema(fields=[fields.ObjectField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.ObjectField
```
