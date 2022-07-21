## `checklist`
{% for check in checklist.checks %}
{% for property, value in check.items() %}
    {% if property == 'type' %}
    ### `{{ value }}`
    {% endif %}
        - `{{ property }}` {{ value }}
{% endfor %}
{% endfor %}