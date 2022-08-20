# Row Errors

{% set errors = frictionless.platform.frictionless_errors %}
{% set exclude = [errors.CellError] %}
{% for Error in errors.RowError.list_children(root=True, exclude=exclude) %}
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

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=RowError
name: frictionless.errors.RowError
```
