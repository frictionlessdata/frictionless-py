---
script:
  basepath: data
---

# Pandas Format

Frictionless supports reading and writing Pandas dataframes.

```bash tabs=CLI
pip install frictionless[pandas]
pip install 'frictionless[pandas]' # for zsh shell
```

## Reading Data

You can read a Pandas dataframe:

```python tabs=Python
from frictionless import Resource

resource = Resource(df)
pprint(resource.read_rows())
```

## Writing Data

You can write a dataset to Pandas:

```python tabs=Python
from frictionless import Resource

resource = Resource('table.csv')
df = resource.to_pandas()
```
