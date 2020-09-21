# Schemes Reference

It's a schemes reference supported by the main Frictionless package. If you have installed external plugins, there can be more schemes available. Below we're listing a scheme group name (or a loader name) like Remote, which is used, for example, for `http`, `https` etc schemes. Options can be used for creating controls, for example, `control = RemoteControl(http_timeout=1)`.

{% for scheme in schemes %}
## {{ scheme.name }}

{% if scheme.options %}
### Options
{% for option in scheme.options %}
#### {{ option.name }}

> Type: {{ option.type }}

{{ option.text }}
{% endfor %}
{% else %}
There are no options available.
{% endif %}
{% endfor %}
