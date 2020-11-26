# Formats Reference

It's a formats reference supported by the main Frictionless package. If you have installed external plugins, there can be more formats available. Below we're listing a format group name (or a parser name) like Excel, which is used, for example, for `xlsx`, `xls` etc formats. Options can be used for creating dialects, for example, `dialect = ExcelDialect(sheet=1)`.

{% for format in formats %}
## {{ format.name }}

{% if format.options %}
### Options
{% for option in format.options %}
#### {{ option.name }}

> Type: {{ option.type }}

{{ option.text }}
{% endfor %}
{% else %}
There are no options available.
{% endif %}
{% endfor %}
