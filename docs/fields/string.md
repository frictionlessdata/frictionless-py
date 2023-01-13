# String Field

## Overview

The field contains strings, that is, sequences of characters. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#string). Currently supported formats:
- default
- uri
- email
- uuid
- binary
- wkt (doesn't work in Python3.10+)

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['value']]
rows = extract(data, schema=Schema(fields=[fields.StringField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.StringField
```
