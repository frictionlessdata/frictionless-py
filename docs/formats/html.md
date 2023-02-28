---
script:
  basepath: data
---

# Html Format

Frictionless supports parsing HTML format:

```bash tabs=CLI
pip install frictionless[html]
pip install 'frictionless[html]' # for zsh shell
```

## Reading Data

You can this file format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import resources

resource = resources.TableResource(path='table1.html')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python script tabs=Python
from frictionless import Resource, resources

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = resources.TableResource(path='table-output.html')
source.write(target)
print(target)
print(target.to_view())
```

## Configuration

There is a dialect to configure HTML, for example:

```python script tabs=Python
from frictionless import Resource, resources, formats

control=formats.HtmlControl(selector='#id')
resource = resources.TableResource(path='table1.html', control=control)
print(resource.read_rows())
```

## Reference

```yaml reference
references:
  - frictionless.formats.HtmlControl
```
