---
script:
  basepath: data
---

# Json Resource

A `json` resource contains a structured data like JSON or YAML (can be validated with JSONSchema -- under development):

```python script tabs=Python
from frictionless.resources import JsonResource

resource = JsonResource(path='data.json')
resource.infer(stats=True)
print(resource)
```

We can read the contents:

```python script tabs=Python
from frictionless.resources import JsonResource

resource = JsonResource(path='data.json')
resource.infer(stats=True)
print(resource.read_data())
```
