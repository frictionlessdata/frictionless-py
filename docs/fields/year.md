# Year Field

## Overview

A calendar year as per XMLSchema gYear. Usual lexical representation is YYYY. There are no format options. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#year).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['2022']]
rows = extract(data, schema=Schema(fields=[fields.YearField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.YearField
```
