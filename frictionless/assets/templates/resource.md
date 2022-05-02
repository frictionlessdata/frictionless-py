## `{{resource.name}}`{% if resource.title %} {{resource.title}}{% endif %}

{% if resource.description %}
  - `description` {{ resource.description | indent(4, False) }}
{% endif %}
{% if resource.path %}
  - `path` {{ resource.path }}
{% endif %}
{% if resource.schema %}
  - `schema`
  {{ resource.schema | filter_dict(exclude=['fields']) | dict_to_markdown(level=2) }}
  {% for field in resource.schema.fields %}
    {% include 'field.md' %}
  {% endfor %}
{% endif %}
