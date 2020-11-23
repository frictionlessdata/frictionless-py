# Working with SPSS

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1znUU6qTXdh2vO7Q9fAec8IUIEia0SqqL)



> Status: **PLUGIN / EXPERIMENTAL**

Frictionless supports reading and writing SPSS files.


```bash
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

You can write SPSS files:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(basepath='target')
```

## Configuring SPSS

> Not supported yet