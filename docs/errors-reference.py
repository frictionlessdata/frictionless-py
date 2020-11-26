import sys
from jinja2 import Template
from frictionless import errors

TEMPLATE = """
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
"""

template = Template(TEMPLATE)
Errors = [item for item in vars(errors).values() if hasattr(item, "code")]
document = template.render(Errors=Errors).strip()
sys.stdout.write(document)
