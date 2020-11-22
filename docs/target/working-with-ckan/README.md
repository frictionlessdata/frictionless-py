# Working with CKAN

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1NrInE94OamiLGmlAlGQ6kmwwGmnA5iav)



>Status: **PLUGIN / EXPERIMENTAL**

Frictionless supports reading and writing CKAN datasets.


```bash
! pip install frictionless[ckan]
```

    Collecting frictionless[ckan]
    [?25l  Downloading https://files.pythonhosted.org/packages/fc/4b/9026ad9f81067bc77bb9609bea0cfc91b258708b2abb9a38aac808801bc0/frictionless-3.33.1-py2.py3-none-any.whl (214kB)
    [K     |████████████████████████████████| 215kB 11.3MB/s
    [?25hCollecting ijson>=3.0
    [?25l  Downloading https://files.pythonhosted.org/packages/6b/b4/2116fef38b2e1701403e7a29dec0d9f9fcc31f1fc95b885581a40915e7fe/ijson-3.1.2.post0-cp36-cp36m-manylinux2010_x86_64.whl (127kB)
    [K     |████████████████████████████████| 133kB 18.9MB/s
    [?25hRequirement already satisfied: requests>=2.10 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (2.23.0)
    Requirement already satisfied: python-dateutil>=2.8 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (2.8.1)
    Collecting jsonlines>=1.2
      Downloading https://files.pythonhosted.org/packages/4f/9a/ab96291470e305504aa4b7a2e0ec132e930da89eb3ca7a82fbe03167c131/jsonlines-1.2.0-py2.py3-none-any.whl
    Collecting stringcase>=1.2
      Downloading https://files.pythonhosted.org/packages/f3/1f/1241aa3d66e8dc1612427b17885f5fcd9c9ee3079fc0d28e9a3aeeb36fa3/stringcase-1.2.0.tar.gz
    Requirement already satisfied: jsonschema>=2.5 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (2.6.0)
    Collecting pyyaml>=5.3
    [?25l  Downloading https://files.pythonhosted.org/packages/64/c2/b80047c7ac2478f9501676c988a5411ed5572f35d1beff9cae07d321512c/PyYAML-5.3.1.tar.gz (269kB)
    [K     |████████████████████████████████| 276kB 21.8MB/s
    [?25hCollecting simpleeval>=0.9
      Downloading https://files.pythonhosted.org/packages/62/25/aec98426834844b70b7ab24b4cce8655d31e654f58e1fa9861533f5f2af1/simpleeval-0.9.10.tar.gz
    Collecting unicodecsv>=0.14
      Downloading https://files.pythonhosted.org/packages/6f/a4/691ab63b17505a26096608cc309960b5a6bdf39e4ba1a793d5f9b1a53270/unicodecsv-0.14.1.tar.gz
    Collecting xlrd>=1.2
    [?25l  Downloading https://files.pythonhosted.org/packages/b0/16/63576a1a001752e34bf8ea62e367997530dc553b689356b9879339cf45a4/xlrd-1.2.0-py2.py3-none-any.whl (103kB)
    [K     |████████████████████████████████| 112kB 32.8MB/s
    [?25hCollecting simplejson>=3.10
    [?25l  Downloading https://files.pythonhosted.org/packages/73/96/1e6b19045375890068d7342cbe280dd64ae73fd90b9735b5efb8d1e044a1/simplejson-3.17.2-cp36-cp36m-manylinux2010_x86_64.whl (127kB)
    [K     |████████████████████████████████| 133kB 26.3MB/s
    [?25hRequirement already satisfied: xlwt>=1.2 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (1.3.0)
    Collecting rfc3986>=1.4
      Downloading https://files.pythonhosted.org/packages/78/be/7b8b99fd74ff5684225f50dd0e865393d2265656ef3b4ba9eaaaffe622b8/rfc3986-1.4.0-py2.py3-none-any.whl
    Collecting openpyxl>=3.0
    [?25l  Downloading https://files.pythonhosted.org/packages/5c/90/61f83be1c335a9b69fa773784a785d9de95c7561d1661918796fd1cba3d2/openpyxl-3.0.5-py2.py3-none-any.whl (242kB)
    [K     |████████████████████████████████| 245kB 31.5MB/s
    [?25hCollecting isodate>=0.6
    [?25l  Downloading https://files.pythonhosted.org/packages/9b/9f/b36f7774ff5ea8e428fdcfc4bb332c39ee5b9362ddd3d40d9516a55221b2/isodate-0.6.0-py2.py3-none-any.whl (45kB)
    [K     |████████████████████████████████| 51kB 5.9MB/s
    [?25hCollecting petl>=1.6
    [?25l  Downloading https://files.pythonhosted.org/packages/da/d0/2f3a75f682b75f23223bdea7846a642d6a130a8f5d5c26986661c4be0442/petl-1.6.8.tar.gz (236kB)
    [K     |████████████████████████████████| 245kB 32.6MB/s
    [?25h  Installing build dependencies ... [?25l[?25hdone
      Getting requirements to build wheel ... [?25l[?25hdone
        Preparing wheel metadata ... [?25l[?25hdone
    Requirement already satisfied: chardet>=3.0 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (3.0.4)
    Collecting typer[all]>=0.3
      Downloading https://files.pythonhosted.org/packages/90/34/d138832f6945432c638f32137e6c79a3b682f06a63c488dcfaca6b166c64/typer-0.3.2-py3-none-any.whl
    Requirement already satisfied: python-slugify>=1.2 in /usr/local/lib/python3.6/dist-packages (from frictionless[ckan]) (4.0.1)
    Collecting ckanapi>=4.3; extra == "ckan"
      Downloading https://files.pythonhosted.org/packages/42/32/1bf732570b30f13eee18189c426754dfb14e231285e6173aaa0b0c33e2da/ckanapi-4.5.tar.gz
    Requirement already satisfied: idna<3,>=2.5 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[ckan]) (2.10)
    Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[ckan]) (2020.6.20)
    Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[ckan]) (1.24.3)
    Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.6/dist-packages (from python-dateutil>=2.8->frictionless[ckan]) (1.15.0)
    Requirement already satisfied: et-xmlfile in /usr/local/lib/python3.6/dist-packages (from openpyxl>=3.0->frictionless[ckan]) (1.0.1)
    Requirement already satisfied: jdcal in /usr/local/lib/python3.6/dist-packages (from openpyxl>=3.0->frictionless[ckan]) (1.4.1)
    Requirement already satisfied: click<7.2.0,>=7.1.1 in /usr/local/lib/python3.6/dist-packages (from typer[all]>=0.3->frictionless[ckan]) (7.1.2)
    Collecting shellingham<2.0.0,>=1.3.0; extra == "all"
      Downloading https://files.pythonhosted.org/packages/9f/6b/160e80c5386f7820f0a9919cc9a14e5aef2953dc477f0d5ddf3f4f2b62d0/shellingham-1.3.2-py2.py3-none-any.whl
    Collecting colorama<0.5.0,>=0.4.3; extra == "all"
      Downloading https://files.pythonhosted.org/packages/44/98/5b86278fbbf250d239ae0ecb724f8572af1c91f4a11edf4d36a206189440/colorama-0.4.4-py2.py3-none-any.whl
    Requirement already satisfied: text-unidecode>=1.3 in /usr/local/lib/python3.6/dist-packages (from python-slugify>=1.2->frictionless[ckan]) (1.3)
    Requirement already satisfied: setuptools in /usr/local/lib/python3.6/dist-packages (from ckanapi>=4.3; extra == "ckan"->frictionless[ckan]) (50.3.2)
    Requirement already satisfied: docopt in /usr/local/lib/python3.6/dist-packages (from ckanapi>=4.3; extra == "ckan"->frictionless[ckan]) (0.6.2)
    Building wheels for collected packages: petl
      Building wheel for petl (PEP 517) ... [?25l[?25hdone
      Created wheel for petl: filename=petl-1.6.8-cp36-none-any.whl size=212569 sha256=06118d2b0cb7f3b292431d708663fb1eafad7deddc2c678055c43b2a16f19134
      Stored in directory: /root/.cache/pip/wheels/ad/29/28/32b02598dd90d47431a6a619aca6de2099778d63e9a68b49ea
    Successfully built petl
    Building wheels for collected packages: stringcase, pyyaml, simpleeval, unicodecsv, ckanapi
      Building wheel for stringcase (setup.py) ... [?25l[?25hdone
      Created wheel for stringcase: filename=stringcase-1.2.0-cp36-none-any.whl size=3578 sha256=e009cff3db0bb6bba6aa6bb4a7c68c4023fa82916842e68222cf7c229195c502
      Stored in directory: /root/.cache/pip/wheels/a0/16/a0/16e2c81dbd47503b5a35583dfabde5a93b4cf98dbf0033dad5


## Reading from CKAN

You can read a CKAN dataset:

```python
from frictionless import Package

package = Package.from_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to CKAN

You can write a dataset to CKAN:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
```

## Configuring CKAN

> CKAN dialect is not yet available