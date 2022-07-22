## `pipeline`
{% for property, value in pipeline.items() %}
{% if property == 'steps' %}
    {% for step in value %}        
        {% include 'step.md' %}
    {% endfor %}
{% else %}
- `{{ property }}` {{ value }}
{% endif %}
{% endfor %}

