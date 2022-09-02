# `{{ package.name }}`{% if package.title %} {{ package.title }}{% endif %}
{{ package | filter_dict(exclude=['name', 'title', 'resources', 'contributor']) | dict_to_markdown() }}
{% for resource in package.resources %}
  {% include 'resource-table.md' %}
{% endfor %}