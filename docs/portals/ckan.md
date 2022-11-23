# Ckan Portal

With CKAN portal feature you can load and publish packages from a [CKAN](https://ckan.org), an open-source Data Management System.

# Installation

To install this plugin you need to do:

```bash tabs=CLI
pip install frictionless[ckan] --pre
pip install 'frictionless[ckan]' --pre # for zsh shell
```

# Configuring the CKAN control

The first thing that you need to do before trying to load a package from CKAN is configure a CKAN control. For that you can import `CkanControl` 
and pass the base URL from your CKAN instance. 

```python tabs=Python
from frictionless.portals import CkanControl

ckan_control = CkanControl(baseurl='https://dados.gov.br')
```

# Reading a package


# Publishing a package

# Reading a Catalog

# Reference

```yaml reference
references:
  - frictionless.portals.CkanControl
```

