# Pandas Format

> This functionality requires an experimental `pandas` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports reading and writing Pandas dataframes.

```bash title="CLI"
pip install frictionless[pandas]
pip install 'frictionless[pandas]' # for zsh shell
```

## Reading Data

You can read a Pandas dataframe:

```python title="Python"
from frictionless import Resource

resource = Resource(df)
pprint(resource.read_rows())
```

## Writing Data

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write a dataset to Pandas:

```python
from frictionless import Resource

resource = Resource('data/table.csv')
df = resource.to_pandas()
```

## Configuring Data

There are no options available in `PandasDialect`.

References:
- [Pandas Dialect](../../references/formats-reference.md#pandas)
