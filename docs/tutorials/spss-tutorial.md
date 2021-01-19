---
title: SPSS Tutorial
---

:::caution Status
Plugin: **EXPERIMENTAL**
:::

Frictionless supports reading and writing SPSS files.

```shell
! pip install frictionless[spss]
```


## Reading from SPSS

You can read SPSS files:

```python
from frictionless import Package

package = Package.from_pandas(basepath='<dir with your .SAV files>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Wriring to SPSS

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write SPSS files:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(basepath='target')
```


## Configuring SPSS

There are no options available in `SpssDialect`.

References:
- [SPSS Dialect](https://frictionlessdata.io/tooling/python/dialects-reference/#spss)
