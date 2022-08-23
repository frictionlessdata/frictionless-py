# File Errors

{% set errors = frictionless.platform.frictionless_errors %}
{% for Error in errors.FileError.list_children(root=True) %}
## {{ Error.title }}

| Name        | Value                      |
| ----------- | -------------------------- |
| Type        | {{ Error.type }}           |
| Title       | {{ Error.title }}          |
| Description | {{ Error.description }}    |
| Template    | {{ Error.template }}       |
| Tags        | {{ Error.tags|join(' ') }} |
{% endfor %}

## Reference

```yaml reference
references:
  - frictionless.errors.FileError
```
