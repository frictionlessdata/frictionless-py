# Array Field

## Overview

The field contains data that is a valid JSON format arrays. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#array).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['["value1", "value2"]']]
rows = extract(data, schema=Schema(fields=[fields.ArrayField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.ArrayField
```
