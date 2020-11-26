# Errors Reference

> This work is based on [Data Quality Spec](https://github.com/frictionlessdata/data-quality-spec)

This document provides a full reference to the Frictionless errors.
{% for Error in Errors %}
## {{ Error.name }}

Code: `{{ Error.code }}` <br>
Tags: `{{ Error.tags|join(' ') or '-' }}` <br>
Template: `{{ Error.template }}` <br>
Description: `{{ Error.description }}` <br>

{% endfor %}
