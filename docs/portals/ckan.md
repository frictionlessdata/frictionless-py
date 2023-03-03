# Ckan Portal

With CKAN portal feature you can load and publish packages from a
[CKAN](https://ckan.org), an open-source Data Management System.

## Installation

To install this plugin you need to do:

```bash tabs=CLI
pip install frictionless[ckan] --pre
pip install 'frictionless[ckan]' --pre # for zsh shell
```

## Reading a Package

To import a Dataset from a CKAN instance as a Frictionless Package you can do
as below:

```python tabs=Python
from frictionless.portals import CkanControl
from frictionless import Package

ckan_control = CkanControl()
package = Package('https://legado.dados.gov.br/dataset/bolsa-familia-pagamentos', control=ckan_control)
```

Where 'https://legado.dados.gov.br/dataset/bolsa-familia-pagamentos' is the URL for
the CKAN dataset. This will download the dataset and all its resources
metadata.

You can pass parameters to CKAN Control to configure it, like the CKAN instance
base URL (`baseurl`) and the dataset that you do want to download (`dataset`):

```python tabs=Python
from frictionless.portals import CkanControl
from frictionless import Package

ckan_control = CkanControl(baseurl='https://legado.dados.gov.br', dataset='bolsa-familia-pagamentos')
package = Package(control=ckan_control)
```

You don't need to pass the `dataset` parameter to CkanControl. In the case that
you pass only the `baseurl` you can download a package as:

```python tabs=Python
from frictionless.portals import CkanControl
from frictionless import Package

ckan_control = CkanControl(baseurl='https://legado.dados.gov.br')
package = Package('bolsa-familia-pagamentos', control=ckan_control)
```

## Ignoring a Resource Schema

In case that the CKAN dataset has a resource containing errors in its schema,
you still can load the package passing the parameter `ignore_schema=True` to
CKAN Control:

```python tabs=Python
from frictionless.portals import CkanControl
from frictionless import Package

ckan_control = CkanControl(baseurl='https://legado.dados.gov.br', ignore_schema=True)
package = Package('bolsa-familia-pagamentos', control=ckan_control)
```

This will download the dataset and all its resources, saving the resources'
original schemas on `original_schema`.

## Publishing a package

To publish a Package to a CKAN instance you will need an API key from an CKAN's
user that has permission to create datasets. This key can be passed to CKAN
Control as the parameter `apikey`.

```python tabs=Python
from frictionless.portals import CkanControl
from frictionless import Package

ckan_control = CkanControl(baseurl='https://legado.dados.gov.br', apikey='YOUR-SECRET-API-KEY')
package = Package(...) # Create your package
package.publish(control=ckan_control)
```

## Reading a Catalog

You can download a list of CKAN datasets using the Catalog.

```python tabs=Python

import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br')
c = Catalog(control=ckan_control)
```

This will download all datasets from the instance, limited only by the maximum
number of datasets returned by the instance CKAN API. If the instance returns
only 10 datasets as default, you can request more packages passing the
parameter `num_packages`. In the example above if you want to download 1000
datasets you can do as:

```python tabs=Python

import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', num_packages=1000)
c = Catalog(control=ckan_control)
```

It's possible that when you are requesting a large number of packages from
CKAN, that some of them don't have a valid Package descriptor according to the
specifications. In that case the standard behaviour will be to stop downloading
a raise an exception. If you want to ignore individual package errors, you can
pass the parameter `ignore_package_errors=True`:


```python tabs=Python

import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', ignore_package_errors=True, num_packages=1000)
c = Catalog(control=ckan_control)
```

And the output of the command above will be the CKAN datasets ids with errors
and the total number of packages returned by your query to the CKAN instance:

```
Error in CKAN dataset 8d60eff7-1a46-42ef-be64-e8979117a378: [package-error] The data package has an error: descriptor is not valid (The data package has an error: property "contributors[].email" is not valid "email")
Error in CKAN dataset 933d7164-8128-4e12-97e6-208bc4935bcb: [package-error] The data package has an error: descriptor is not valid (The data package has an error: property "contributors[].email" is not valid "email")
Error in CKAN dataset 93114fec-01c2-4ef5-8dfe-67da5027d568: [package-error] The data package has an error: descriptor is not valid (The data package has an error: property "contributors[].email" is not valid "email") (The data package has an error: property "contributors[].email" is not valid "email")
Total number of packages: 13786
```

You can see in the example above that 1000 packages were download from a total
13786 packages. You can download other packages passing an offset as:

```python tabs=Python

import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', ignore_package_erros=True, results_offset=1000)
c = Catalog(control=ckan_control)
```

This will download 1000 packages after the the first 1000 packages.

## Fetching the datasets from an Organization or Group

To fetch all packages from a organization will can use the CKAN Control
parameter `organization_name`. e.g. if you want to fetch all datasets from the
organization `https://legado.dados.gov.br/organization/agencia-espacial-brasileira-aeb` you can do
as follows:


```python tabs=Python
import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', organization_name='agencia-espacial-brasileira-aeb')
c = Catalog(control=ckan_control)
```

Similarly, if you want to download all datasets from a CKAN Group you can pass
the parameter `group_id` to the CKAN Control as:

```python tabs=Python
import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', group_id='ciencia-informacao-e-comunicacao')
c = Catalog(control=ckan_control)
```

## Using CKAN search

You can also fetch only the datasets that are returned by the [CKAN Package
Search endpoint](https://docs.ckan.org/en/2.9/api/#ckan.logic.action.get.package_search).
You can pass the search parameters as the parameter `search` to CKAN Control.

```python tabs=Python
import frictionless
from frictionless import portals, Catalog

ckan_control = portals.CkanControl(baseurl='https://legado.dados.gov.br', search={'q': 'name:bolsa*'})
c = Catalog(control=ckan_control)
```

## Reference

```yaml reference
references:
  - frictionless.portals.CkanControl
```
