---
title: Working in Python
---

Frictionless Framework is a Python framework so it's naturally to be used within a Python programming environment.

## Install

To install the package please follow the [Quick Start](../guides/quick-start.md) guide.

## Import

The package in Python is exposed as a single module called `frictionless`.

### Core

After installation you can import and use it to access the core functionality:

```python title="Python"
import frictionless

frictionless.Schema
frictionless.Resource
frictionless.Package
# etc
```

Another option is to used named import:

```python title="Python"
from frictionless import Schema, Resource, Package

Schema
Resource
Package
# etc
```

Frictionless has a reach API including high-level functions and classes. You can find a full list in the [API Reference](../references/api-reference.md).

### Plugins

Frictionless ships with more than dozen builtin plugins. Usually you don't need to use them directly as it will be inferred and handled automatically, but, in some cases, you need to import their classes. For example:

```python title="Python"
from frictionless.plugins.csv import CsvDialect

CsvDialect
```

## Debug

All the metadata classes inherit from the `dict` type so you can just print it:

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource('data/table.csv')
resource.infer()
pprint(resource)
# Prints metadata dict i.e. path, schema, etc
```

For tabular resource you can also use the `resource.to_view()` function for pretty-printing tables:

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource('data/table.csv')
pprint(resource.to_view())
# Prints a pretty-formatted data table
pprint(resource.read_rows())
# Of course, you can always just use `resource.read_rows()` or other reading functions:
```

## Errors

Frictionless uses a unifed error tree but there is only one exception `frictionless.FrictionlessException` so you need to catch this one and analyze an attached error:

```python title="Python"
from pprint import pprint
from frictionless import Resource, FrictionlessException

try:
    resource = Resource('bad.csv')
except FrictionlessException as exception:
    pprint(exception.error)
    # Prints the SchemaError metadata in this case
```

If you got some other exception using the Frictionless codebase it might be a bug so please report it to the [Issue Tracker](https://github.com/frictionlessdata/frictionless-py/issues).

## Hints

Working with Frictionless in some modern Code Editor or interactive Notebook you can use code hints/completion capability. For example, there are many transform steps available, to find a right one just start typing:

```python title="Python"
from frictionless import steps

steps.table_<TAB>
# Code completion will show the list of available table steps
```

The same works for class' and functions' arguments:

```python title="Python"
from frictionless import Resource

Resource('data/table.csv, <TAB>
# Code completion will show the list of available arguments steps
```
