### `{{ field.name }}`{% if field.title %} {{ field.title }}{% endif %}
{{ '\n' }}
{% if field.description %}
  - `description` {{ field.description | indent(4, False) }}
{% endif %}
{% if field.type %}
  - `type` {{ field.type }}
{% endif %}
{% if field.constraints %}
  - `constraints`:
  {% for key, value in field.constraints.items() if value %}
    {% if key == 'pattern' %}
    - `{{ key }}` `{{ value }}`
    {% else %}
    - `{{ key }}` {{ value }}
    {% endif %}
  {% endfor %}
{% endif %}