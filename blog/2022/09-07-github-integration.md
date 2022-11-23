---
script:
  basepath: data
blog:
  author: Shashi Gharti
  image: ../assets/github.png
  description: This blog gives the introduction of the github plugin which helps to seamlessly transfer/read data to/from Github.
---

# Github Integration

We are happy to announce github plugin which makes sharing data between frictionless and github easier without any extra work and configuration. All the github plugin functionalities are wrapped around the PyGithub library. The main idea is to make the interaction between the framework and github seamless using read and write functions developed on top of the Frictionless python library. Here is a short introduction and examples of the features.

## Reading from the repo

Reading package from github repository is made easy! The existing ```Package``` class can identify the github url and read the packages and resources from the repo. It can read packages from repos with or without packages descriptors. If a package descriptor is not defined, it will create a package descriptor with resources that it finds in the repo.

```python tabs=Python
from frictionless import Package

package = Package("https://github.com/fdtester/test-repo-with-datapackage-json")
print(package)
```

## Writing/Publishing to the repo

Writing and publishing can be easily done by passing the repository link using `publish` function.

```python tabs=Python
from frictionless import Package, portals

apikey = 'YOUR-GITHUB-API-KEY'
package = Package('data/datapackage.json')
response = package.publish("https://github.com/fdtester/test-repo-write",
        control=portals.GithubControl(apikey=apikey)
    )
```

## Creating catalog

Catalog can be created from a single repository by using 'search' queries. Repositories can be searched using combination of any search text and github qualifiers. A simple example of creating catalog from search is as follows:

```python tabs=Python
from frictionless import Catalog, portals

catalog = Catalog(
        control=portals.GithubControl(search="user:fdtester", per_page=1, page=1),
    )
```


### Happy Contributors

We will have more updates in future and would love to hear from you about this new feature. Let's chat in our [Slack](https://join.slack.com/t/frictionlessdata/shared_invite/zt-17kpbffnm-tRfDW_wJgOw8tJVLvZTrBg) if you have questions or just want to say hi.

Read [Github Plugin Docs](../../docs/portals/github.html) for more information.
