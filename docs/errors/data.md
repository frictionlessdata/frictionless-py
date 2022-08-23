# Data Errors

{% set errors = frictionless.platform.frictionless_errors %}
{% set exclude = [errors.FileError, errors.TableError] %}
{% for Error in errors.DataError.list_children(root=True, exclude=exclude) %}
## {{ Error.title }}

| Name        | Value                      |
| ----------- | -------------------------- |
| Type        | {{ Error.type }}           |
| Title       | {{ Error.title }}          |
| Description | {{ Error.description }}    |
| Template    | {{ Error.template }}       |
{% endfor %}

## Reference

```yaml reference
references:
  - frictionless.errors.DataError
```
