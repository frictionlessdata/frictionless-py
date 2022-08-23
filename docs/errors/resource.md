# Resource Errors

{% set errors = frictionless.platform.frictionless_errors %}
{% for Error in errors.ResourceError.list_children(root=True) %}
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
  - frictionless.errors.ResourceError
```
