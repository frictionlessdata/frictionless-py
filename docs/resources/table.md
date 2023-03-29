---
script:
  basepath: data
---

# Table Resource

A `table` resource contains a tabular data file (can be validated with Table Schema):

```python script tabs=Python
from frictionless.resources import TableResource

resource = TableResource(path='table.csv')
resource.infer(stats=True)
print(resource)
```

We can read the contents:

```python script tabs=Python
from frictionless.resources import TableResource

resource = TableResource(path='table.csv')
resource.infer(stats=True)
print(resource.read_rows())
```
