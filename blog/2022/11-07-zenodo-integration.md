---
script:
  basepath: data
blog:
  author: Shashi Gharti
  image: ../assets/zenodo.png
  description: This blog gives the introduction of the zenodo plugin which helps to easily read data from and write data to Zenodo.
---

# Zenodo Integration

Zenodo integration was very highly requested feature and we are happy to share our first draft of the plugin which makes sharing data between frictionless and zenodo easier without any extra work and configuration. This plugin uses zenodopy library underneath to communicate with Zenodo REST API. A frictionless user can use the framework functionalities and then easily publish data to zenodo and viceversa. Here is a short description of the features with examples.

## Reading from the repo

You can simply read the package or create a new package from the zenodo repository if package does not exists. No additional configuration is required. The existing ```Package``` class identifies zenodo url and reads the packages and resources from the repo. Example of reading package from the zenodo repo is as follows:

```python tabs=Python
from frictionless import Package

package = Package("https://zenodo.org/record/7078760")
print(package)
```

Once read you can apply all the available functions to the package such as validation, transformation etc.

## Writing/Publishing to the repo

To write the package we can simply use `publish` function, which will write the package and resource files to zenodo repository. We need to provide meta data for the repository while publishing data which we pass as meta.json as shown in the example below:

```python tabs=Python
from frictionless import Package, portals

control = portals.ZenodoControl(
       metafn="data/zenodo/metadata.json",
       apikey=apikey
)
package = Package("data/datapackage.json")
deposition_id = package.publish(control=control)
print(deposition_id)

```
Once the package is published, deposition_id will be returned.

## Creating catalog

Catalog can be created from a single repository or from multiple repositories. Repositories can be searched using any search terms, phrase, field search or combination of all. A simple example of creating catalog from search is as follows:

```python tabs=Python
from frictionless import Catalog, portals
control=portals.ZenodoControl(search='title:"open science"')
catalog = Catalog(
        control=control,
    )
```


### Happy Contributors

We will have more updates in future and would love to hear from you about this new feature. Let's chat in our [Slack](https://join.slack.com/t/frictionlessdata/shared_invite/zt-17kpbffnm-tRfDW_wJgOw8tJVLvZTrBg) if you have questions or just want to say hi.

Read [Zenodo Plugin Docs](../../docs/portals/zenodo.html) for more information.
