---
script:
  basepath: data
---

# Parquet Format

Frictionless supports reading and writing Parquet files.

```bash tabs=CLI
pip install frictionless[parquet]
pip install 'frictionless[parquet]' # for zsh shell
```

## Reading Data

You can read a Parquet file:

```python script tabs=Python
from frictionless import Resource

resource = Resource('table.parq')
print(resource.read_rows())
```

## Writing Data

You can write a dataset to Parquet:

```python script tabs=Python
from frictionless import Resource

resource = Resource('table.csv')
target = resource.write('table-output.parq')
print(target)
print(target.read_rows())
```

## Reference

```yaml reference
references:
  - frictionless.formats.ParquetControl
```
