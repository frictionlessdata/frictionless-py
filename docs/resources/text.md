---
script:
  basepath: data
---

# Text Resource

A `text` resource represents a textual file as a markdown document, for example:


```python script tabs=Python
from frictionless.resources import TextResource

resource = TextResource(path='article.md')
resource.infer(stats=True)
print(resource)
```

We can read the contents:

```python script tabs=Python
from frictionless.resources import TextResource

resource = TextResource(path='article.md')
resource.infer(stats=True)
print(resource.read_text())
```
