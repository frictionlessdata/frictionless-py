- `tasks` 
    - `task` {% if task.name %} {{ task.name }}{% endif %}

    {% for property, value in task.items() %}
        - `{{ property }}` {{ value }}
    {% endfor %}