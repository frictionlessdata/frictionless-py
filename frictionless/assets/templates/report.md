## `report`
{% for property, value in report.items() %}
{% if property == 'tasks' %}    
    {% for task in value %}
        {% include 'report-task.md' %}
    {% endfor %}
{% else %}
- `{{ property }}` {{ value }}
{% endif %}
{% endfor %}