## `inquiry`
{% for property, value in inquiry.items() %}
{% if property == 'tasks' %}
{% for task in value %}
### `task` {% if task.name %} {{ task.name }}{% endif %}
{% for task_property, task_value in task.items() %}
- `{{ task_property }}` {{ task_value }}
{% endfor %}
{% endfor %}
{% else %}
- `{{ property }}` {{ value }}
{% endif %}
{% endfor %}