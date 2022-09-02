# Table Errors

{% set errors = frictionless.platform.frictionless_errors %}
{% set exclude = [errors.HeaderError, errors.RowError] %}
{% for Error in errors.TableError.list_children(root=True, exclude=exclude) %}
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
  - frictionless.errors.TableError
```
