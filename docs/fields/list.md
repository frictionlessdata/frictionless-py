# List Field

## Overview

The field contains an ordered collection of primitive values of a fixed item type, written as a string with the items separated by a delimiter. Read more in [Table Schema Standard](https://datapackage.org/standard/table-schema/#list).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['1,2,3']]
rows = extract(data, schema=Schema(fields=[fields.ListField(name='name', item_type='integer')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.ListField
```
