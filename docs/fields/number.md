# Number Field

## Overview

The field contains numbers of any kind including decimals. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#number).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['1.1'], ['2.2'], ['3.3']]
rows = extract(data, schema=Schema(fields=[fields.NumberField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.NumberField
```
