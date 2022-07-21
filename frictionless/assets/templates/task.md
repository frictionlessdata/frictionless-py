### `task`
{% for property, value in task.items() %}
{% if property == 'steps' %}
{% for step in value %}        
    {% include 'step.md' %}
{% endfor %}
{% else %}
- `{{ property }}` {{ value }}
{% endif %}
{% endfor %}
