---
title: Pandas Tutorial
sidebar_label: Pandas
---

:::caution
This functionality requires an experimental `pandas` plugin. [Read More](../../references/plugins-reference.md)
:::

Frictionless supports reading and writing Pandas dataframes.

```bash
! pip install frictionless[pandas]
```


## Reading from Pandas

You can read a Pandas dataframe:

```python
from frictionless import Package

package = Package.from_pandas(dataframes=['table1': '<df1>', 'tables2': '<df2>'])
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Writing to Pandas

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write a dataset to Pandas:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
dataframes = package.to_pandas()
```


## Configuring Pandas

There are no options available in `PandasDialect`.

References:
- [Pandas Dialect](../../references/formats-reference.md#pandas)
