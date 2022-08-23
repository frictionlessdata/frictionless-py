# Geopoint Field

The field contains data describing a geographic point. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#geopoint).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ["180, -90"]]
rows = extract(data, schema=Schema(fields=[fields.GeopointField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.GeopointField
```
