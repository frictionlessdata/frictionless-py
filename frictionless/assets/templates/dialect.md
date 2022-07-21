## `dialect`
{% for key, dialect in dialect.items() %}
### `{{ key }}`
{% for property, value in dialect.items() %}
- `{{ property }}` {{ value }}            
{% endfor %}
{% endfor %}