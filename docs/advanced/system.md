# System

```markdown remark type=danger
This feature is currently experimental. The API might change without notice
```

## System Object

The most important undelaying object in the Frictionless Framework is `system`. It's an singleton object avaialble as `frictionless.system`.

## System Context

Using the `system` object a user can alter the execution context. It uses a Python context manager so it can be used in anyway that it's possible in Python, for example, it can be nested or combined.

### trusted

If data or metadata comes from a trusted origin, it's possible to disable safety checks for paths:

```python
with system.use_context(trusted=True):
    extract('/path/to/file/is/absolute.csv')
```

### onerror

To raise warning or errors on data problems, it's possible to use `onerror` context value. It's default to `ignore` and can be set to `warn` or `error`:

```python
with system.use_context(onerror='error'):
    extract('table-with-error-will-raise-an-exeption.csv')
```

### standards

By default, the framework uses coming `v2` version of the standards for outputing metadata. It's possible to alter this behaviour:


```python
with system.use_context(standards='v1'):
    describe('metadata-will-be-in-v1.csv')
```

### http_session

It's possible to provide a custom `requests.Session`:

```python
session = requests.Session()
with system.use_context(http_session=session):
    with Resource(BASEURL % "data/table.csv") as resource:
        assert resource.header == ["id", "name"]
```

## System methods

This object can be used to instantiate different kind of lower-level as though `Check`, `Step`, or `Field`. Here is a quick example of using the `system` object:

```python tabs=Python
from frictionless import Resource, system

# Create

adapter = system.create_adapter(source, control=control)
loader = system.create_loader(resource)
parser = system.create_parser(resource)

# Detect

system.detect_resource(resource)
field_candidates = system.detect_field_candidates()

# Select

Check = system.selectCheck('type')
Control = system.selectControl('type')
Error = system.selectError('type')
Field = system.selectField('type')
Step = system.selectStep('type')
```

As an extension author you might use the `system` object in various cases. For example, take a look at this `MultipartLoader` excerpts:

```python tabs=Python
def read_line_stream(self):
    for number, path in enumerate(self.__path, start=1):
        resource = Resource(path=path)
        resource.infer(sample=False)
        with system.create_loader(resource) as loader:
            for line_number, line in enumerate(loader.byte_stream, start=1):
                if not self.__headless and number > 1 and line_number == 1:
                    continue
                yield line
```

It's important to understand that creating low-level objects in general is more corect using the `system` object than just classes because it will include all the available plugins in the process.

## Plugin API

The Plugin API almost fully follows the system object's API. So as a plugin author you need to hook into the same methods. For example, let's take a look at a builtin Csv Plugin:

```python tabs=Python
class CsvPlugin(Plugin):
    """Plugin for CSV"""

    # Hooks

    def create_parser(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            return CsvParser(resource)

    def detect_resource(self, resource: Resource):
        if resource.format in ["csv", "tsv"]:
            resource.type = "table"
            resource.mediatype = f"text/{resource.format}"

    def select_Control(self, type: str):
        if type == "csv":
            return CsvControl
```

## Reference

```yaml reference
references:
  - frictionless.Adapter
  - frictionless.Loader
  - frictionless.Mapper
  - frictionless.Parser
  - frictionless.Plugin
  - frictionless.System
```
