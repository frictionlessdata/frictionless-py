# Geojson Field

The field contains a JSON object according to GeoJSON or TopoJSON spec. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#geojson).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['{"geometry": null, "type": "Feature", "properties": {"k": "v"}}']]
rows = extract(data, schema=Schema(fields=[fields.GeojsonField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.GeojsonField
```
