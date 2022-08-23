# Integer Field

The field contains integers - that is whole numbers. Integer values are indicated in the standard way for any valid integer. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#integer).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['1'], ['2'], ['3']]
rows = extract(data, schema=Schema(fields=[fields.IntegerField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.IntegerField
```
