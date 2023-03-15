---
script:
  basepath: data
---

# File Resource

A `file` resource is the most basic one. Actually, every data file can be maked as `file`. For example:


```python script tabs=Python
from frictionless.resources import FileResource

resource = FileResource(path='text.txt')
resource.infer(stats=True)
print(resource)
```
