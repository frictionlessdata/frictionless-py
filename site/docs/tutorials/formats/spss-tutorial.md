---
title: SPSS Tutorial
sidebar_label: SPSS
---

> This functionality requires an experimental `spss` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports reading and writing SPSS files.

```bash title="CLI"
pip install frictionless[spss]
pip install 'frictionless[spss]' # for zsh shell
```

## Reading Data

You can read SPSS files:

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource('data/table.sav')
pprint(resource.read_rows())
```

## Writing Data

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write SPSS files:

```python title="Python"
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.sav')
pprint(target)
pprint(target.read_rows())
```

## Configuring Data

There are no options available in `SpssDialect`.

References:
- [SPSS Dialect](../../references/formats-reference.md#spss)
