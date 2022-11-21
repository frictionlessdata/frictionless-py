# Github Portal

Github read and publish feature makes easy to share data between frictionless and the github repositories. All read/write functionalities are the wrapper around PyGithub library which is used under the hood to make connection to github api.

## Installation

We need to install github extra dependencies to use this feature:

```bash tabs=CLI
pip install frictionless[github] --pre
pip install 'frictionless[github]' --pre # for zsh shell
```

## Reading Package

You can read data from a github repository as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://github.com/fdtester/test-repo-without-datapackage")
print(package)
```
```
{'name': 'test-repo-without-datapackage',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'countries',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'student',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx',
                'scheme': 'https',
                'format': 'xlsx',
                'mediatype': 'application/vnd.ms-excel'}]}
```
You can also use alias function instead, for example:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://github.com/fdtester/test-repo-without-datapackage")
print(package)
```

To increase the access limit, pass 'apikey' as the param to the reader function as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.GithubControl(apikey=apikey)
package = Package("https://github.com/fdtester/test-repo-without-datapackage", control=control)
print(package)
```

The `reader` function can read package from repos with/without data package descriptor. If the repo does not have the descriptor it will create the descriptor with the name same as the repo name as shown in the example above. By default, the function reads files of type csv, xlsx and xls but we can set the file types using control parameters.

If the repo has a descriptor it simply returns the descriptor as shown below

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://https://github.com/fdtester/test-repo-with-datapackage-json")
```
```
print(package)
{'name': 'test-tabulator',
 'resources': [{'name': 'first-resource',
                'path': 'table.xls',
                'schema': {'fields': [{'name': 'id', 'type': 'number'},
                                      {'name': 'name', 'type': 'string'}]}},
               {'name': 'number-two',
                'path': 'table-reverse.csv',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}
```
Once you read the package from the repo, you can then easily access the resources and its data, for example:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://github.com/fdtester/test-repo-without-datapackage")
pprint(package.get_resource('capitals').read_rows())
```
```
[{'id': 1, 'cid': 1, 'name': 'London'},
 {'id': 2, 'cid': 2, 'name': 'Paris'},
 {'id': 3, 'cid': 3, 'name': 'Berlin'},
 {'id': 4, 'cid': 4, 'name': 'Rome'},
 {'id': 5, 'cid': 5, 'name': 'Lisbon'}]
```

## Reading Catalog

Catalog is a container for the packages. We can read single/multiple repositories from github and create a catalog.

```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.GithubControl(search="'TestAction: Read' in:readme", apikey=apikey)
catalog = Catalog(
        "https://github.com/fdtester", control=control
    )
print("Total packages", len(catalog.packages))
print(catalog.packages[:2])
```
```
Total packages 4
[{'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'data/capitals.csv',
                'scheme': 'file',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'csv': {'skipInitialSpace': True}},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]},
 {'name': 'test-repo-jquery',
 'resources': [{'name': 'country-1',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-jquery/main/country-1.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}]
```
To read catalog, we need authenticated user so we have to pass the token as 'apikey' to the function. In the above example we are using search text to filter the repositories to small number. The search field is not mandatory.

We can simply use 'control' parameters and get the same result as above, for example:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.GithubControl(search="'TestAction: Read' in:readme", user="fdtester", apikey=apikey)
catalog = Catalog(control=control)
print("Total packages", len(catalog.packages))
print(catalog.packages[:2])
```
As shown in the example above, we can use different qualifiers to search the repos. The above example searches for all the repos which has 'TestAction: Read' text in readme files. Similary we can use many different qualifiers and combination of those. To get full list of qualifiers you can check the github document [here](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories).

Some examples of the qualifiers:

```
‘jquery’ in:name
‘jquery’ in:name user:name
sort:updated-asc ‘TestAction: Read’ in:readme
```
If we want to read the list of repositories of user 'fdtester' which has 'jquery' in its name then we write search query as follows:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.GithubControl(apikey=apikey, search="user:fdtester jquery in:name")
catalog = Catalog(control=control)
print(catalog.packages)
```
```
[{'name': 'test-repo-jquery',
 'resources': [{'name': 'country-1',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-jquery/main/country-1.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}]
```
There is only one repository having 'jquery' in name for this user's account, so it returned only one repository.

We can also read repositories in defined order using 'sort' param or qualifier. Here we are trying to read the repos with 'TestAction: Read' text in readme file in recently updated order, for example:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.GithubControl(apikey=apikey, search="user:fdtester sort:updated-desc 'TestAction: Read' in:readme")
catalog = Catalog(control=control)
for index,package in enumerate(catalog.packages):
    print(f"package:{index}", "\n")
    print(package)
```
```
package:0

{'name': 'test-repo-without-datapackage',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'countries',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'student',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/student.xlsx',
                'scheme': 'https',
                'format': 'xlsx',
                'mediatype': 'application/vnd.ms-excel'}]}
package:1

{'name': 'test-repo-jquery',
 'resources': [{'name': 'country-1',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-jquery/main/country-1.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}
package:2

{'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'data/capitals.csv',
                'scheme': 'file',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'csv': {'skipInitialSpace': True}},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}
package:3

{'name': 'test-tabulator',
 'resources': [{'name': 'first-resource',
                'path': 'table.xls',
                'schema': {'fields': [{'name': 'id', 'type': 'number'},
                                      {'name': 'name', 'type': 'string'}]}},
               {'name': 'number-two',
                'path': 'table-reverse.csv',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}
```

## Publishing Data

To write data to the repository, we use `Package.publish` function as follows:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package('1174/datapackage.json')
control = portals.GithubControl(repo="test-new-repo-doc", name='FD', email=email, apikey=apikey)
response = package.publish(control=control)
print(response)
```
```
Repository(full_name="fdtester/test-new-repo-doc")
```
We need to mention `name` and `email` explicitly if the user doesn't have name set in his github account, and if email is private and hidden. Otherwise, it will take these info from the user account. In order to be able to publish/write to respository, we need to have the api token with 'repository write' access.

If the package is successfully published, the response is a 'Repository' instance.

## Configuration

We can control the behavior of all the above three functions using various params.

For example, to read only 'csv' files in package we use the following code:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.GithubControl(user="fdtester", formats=["csv"], repo="test-repo-without-datapackage", apikey=apikey)
package = Package("https://github.com/fdtester/test-repo-without-datapackage")
print(package)
```
```
{'name': 'test-repo-without-datapackage',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'countries',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}
```

In order to read first page of the search result and create a catalog, we use `per_page` and `page` params as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.GithubControl(apikey=apikey, search="user:fdtester sort:updated-desc 'TestAction: Read' in:readme", per_page=1, page=1)
catalog = Catalog(control=control)
```
```
[{'name': 'test-repo-jquery',
 'resources': [{'name': 'country-1',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-jquery/main/country-1.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}]
```

Similary, we can also control the write function using params as follows:
```
from pprint import pprint
from frictionless import portals, Package

package = Package('datapackage.json')
control = portals.GithubControl(repo="test-repo", name='FD Test', email="test@gmail", apikey=apikey)
response = package.publish(control=control)
print(response)
```
```
Repository(full_name="fdtester/test-repo")
```

## Reference

```yaml reference
references:
  - frictionless.portals.GithubControl
```
