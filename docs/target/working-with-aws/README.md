# Working with AWS

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1JoE1twt8EmyMhFbT76HqDGbXcXMugjS2)



> Status: **PLUGIN / STABLE**

Frictionless supports reading data from S3 cloud storage. You can read file in any format that is available in your bucket.


```bash
!pip install frictionless[aws]
```

    Collecting frictionless[aws]
    [?25l  Downloading https://files.pythonhosted.org/packages/fc/4b/9026ad9f81067bc77bb9609bea0cfc91b258708b2abb9a38aac808801bc0/frictionless-3.33.1-py2.py3-none-any.whl (214kB)
    [K     |████████████████████████████████| 215kB 8.6MB/s
    [?25hCollecting openpyxl>=3.0
    [?25l  Downloading https://files.pythonhosted.org/packages/5c/90/61f83be1c335a9b69fa773784a785d9de95c7561d1661918796fd1cba3d2/openpyxl-3.0.5-py2.py3-none-any.whl (242kB)
    [K     |████████████████████████████████| 245kB 12.0MB/s
    [?25hCollecting isodate>=0.6
    [?25l  Downloading https://files.pythonhosted.org/packages/9b/9f/b36f7774ff5ea8e428fdcfc4bb332c39ee5b9362ddd3d40d9516a55221b2/isodate-0.6.0-py2.py3-none-any.whl (45kB)
    [K     |████████████████████████████████| 51kB 5.0MB/s
    [?25hCollecting typer[all]>=0.3
      Downloading https://files.pythonhosted.org/packages/90/34/d138832f6945432c638f32137e6c79a3b682f06a63c488dcfaca6b166c64/typer-0.3.2-py3-none-any.whl
    Collecting jsonlines>=1.2
      Downloading https://files.pythonhosted.org/packages/4f/9a/ab96291470e305504aa4b7a2e0ec132e930da89eb3ca7a82fbe03167c131/jsonlines-1.2.0-py2.py3-none-any.whl
    Collecting xlrd>=1.2
    [?25l  Downloading https://files.pythonhosted.org/packages/b0/16/63576a1a001752e34bf8ea62e367997530dc553b689356b9879339cf45a4/xlrd-1.2.0-py2.py3-none-any.whl (103kB)
    [K     |████████████████████████████████| 112kB 14.4MB/s
    [?25hCollecting simplejson>=3.10
    [?25l  Downloading https://files.pythonhosted.org/packages/73/96/1e6b19045375890068d7342cbe280dd64ae73fd90b9735b5efb8d1e044a1/simplejson-3.17.2-cp36-cp36m-manylinux2010_x86_64.whl (127kB)
    [K     |████████████████████████████████| 133kB 14.7MB/s
    [?25hRequirement already satisfied: python-dateutil>=2.8 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (2.8.1)
    Collecting rfc3986>=1.4
      Downloading https://files.pythonhosted.org/packages/78/be/7b8b99fd74ff5684225f50dd0e865393d2265656ef3b4ba9eaaaffe622b8/rfc3986-1.4.0-py2.py3-none-any.whl
    Collecting stringcase>=1.2
      Downloading https://files.pythonhosted.org/packages/f3/1f/1241aa3d66e8dc1612427b17885f5fcd9c9ee3079fc0d28e9a3aeeb36fa3/stringcase-1.2.0.tar.gz
    Collecting simpleeval>=0.9
      Downloading https://files.pythonhosted.org/packages/62/25/aec98426834844b70b7ab24b4cce8655d31e654f58e1fa9861533f5f2af1/simpleeval-0.9.10.tar.gz
    Requirement already satisfied: python-slugify>=1.2 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (4.0.1)
    Collecting pyyaml>=5.3
    [?25l  Downloading https://files.pythonhosted.org/packages/64/c2/b80047c7ac2478f9501676c988a5411ed5572f35d1beff9cae07d321512c/PyYAML-5.3.1.tar.gz (269kB)
    [K     |████████████████████████████████| 276kB 13.8MB/s
    [?25hCollecting ijson>=3.0
    [?25l  Downloading https://files.pythonhosted.org/packages/6b/b4/2116fef38b2e1701403e7a29dec0d9f9fcc31f1fc95b885581a40915e7fe/ijson-3.1.2.post0-cp36-cp36m-manylinux2010_x86_64.whl (127kB)
    [K     |████████████████████████████████| 133kB 25.7MB/s
    [?25hCollecting unicodecsv>=0.14
      Downloading https://files.pythonhosted.org/packages/6f/a4/691ab63b17505a26096608cc309960b5a6bdf39e4ba1a793d5f9b1a53270/unicodecsv-0.14.1.tar.gz
    Collecting petl>=1.6
    [?25l  Downloading https://files.pythonhosted.org/packages/da/d0/2f3a75f682b75f23223bdea7846a642d6a130a8f5d5c26986661c4be0442/petl-1.6.8.tar.gz (236kB)
    [K     |████████████████████████████████| 245kB 20.6MB/s
    [?25h  Installing build dependencies ... [?25l[?25hdone
      Getting requirements to build wheel ... [?25l[?25hdone
        Preparing wheel metadata ... [?25l[?25hdone
    Requirement already satisfied: xlwt>=1.2 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (1.3.0)
    Requirement already satisfied: jsonschema>=2.5 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (2.6.0)
    Requirement already satisfied: chardet>=3.0 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (3.0.4)
    Requirement already satisfied: requests>=2.10 in /usr/local/lib/python3.6/dist-packages (from frictionless[aws]) (2.23.0)
    Collecting boto3>=1.9; extra == "aws"
    [?25l  Downloading https://files.pythonhosted.org/packages/4e/31/4d4861a90d66c287a348fd17eaefefcdc2e859951cab9884b555923f046d/boto3-1.16.23-py2.py3-none-any.whl (129kB)
    [K     |████████████████████████████████| 133kB 21.3MB/s
    [?25hRequirement already satisfied: jdcal in /usr/local/lib/python3.6/dist-packages (from openpyxl>=3.0->frictionless[aws]) (1.4.1)
    Requirement already satisfied: et-xmlfile in /usr/local/lib/python3.6/dist-packages (from openpyxl>=3.0->frictionless[aws]) (1.0.1)
    Requirement already satisfied: six in /usr/local/lib/python3.6/dist-packages (from isodate>=0.6->frictionless[aws]) (1.15.0)
    Requirement already satisfied: click<7.2.0,>=7.1.1 in /usr/local/lib/python3.6/dist-packages (from typer[all]>=0.3->frictionless[aws]) (7.1.2)
    Collecting shellingham<2.0.0,>=1.3.0; extra == "all"
      Downloading https://files.pythonhosted.org/packages/9f/6b/160e80c5386f7820f0a9919cc9a14e5aef2953dc477f0d5ddf3f4f2b62d0/shellingham-1.3.2-py2.py3-none-any.whl
    Collecting colorama<0.5.0,>=0.4.3; extra == "all"
      Downloading https://files.pythonhosted.org/packages/44/98/5b86278fbbf250d239ae0ecb724f8572af1c91f4a11edf4d36a206189440/colorama-0.4.4-py2.py3-none-any.whl
    Requirement already satisfied: text-unidecode>=1.3 in /usr/local/lib/python3.6/dist-packages (from python-slugify>=1.2->frictionless[aws]) (1.3)
    Requirement already satisfied: idna<3,>=2.5 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[aws]) (2.10)
    Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[aws]) (1.24.3)
    Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.6/dist-packages (from requests>=2.10->frictionless[aws]) (2020.6.20)
    Collecting botocore<1.20.0,>=1.19.23
    [?25l  Downloading https://files.pythonhosted.org/packages/77/49/c8c99477416fdebb59078bda624acc5b3c7008f891c60d56d6ff1570d83e/botocore-1.19.23-py2.py3-none-any.whl (6.8MB)
    [K     |████████████████████████████████| 6.9MB 22.9MB/s
    [?25hCollecting jmespath<1.0.0,>=0.7.1
      Downloading https://files.pythonhosted.org/packages/07/cb/5f001272b6faeb23c1c9e0acc04d48eaaf5c862c17709d20e3469c6e0139/jmespath-0.10.0-py2.py3-none-any.whl
    Collecting s3transfer<0.4.0,>=0.3.0
    [?25l  Downloading https://files.pythonhosted.org/packages/69/79/e6afb3d8b0b4e96cefbdc690f741d7dd24547ff1f94240c997a26fa908d3/s3transfer-0.3.3-py2.py3-none-any.whl (69kB)
    [K     |████████████████████████████████| 71kB 7.9MB/s
    [?25hBuilding wheels for collected packages: petl
      Building wheel for petl (PEP 517) ... [?25l[?25hdone
      Created wheel for petl: filename=petl-1.6.8-cp36-none-any.whl size=212569 sha256=1afc01a6fdcd2e37ab8813158eb7e06e4df2396d606053d7f7efb6a54b641888
      Stored in directory: /root/.cache/pip/wheels/ad/29/28/32b02598dd90d47431a6a619aca6de2099778d63e9a68b49ea
    Successfully built petl
    Building wheels for collected packages: stringcase, simpleeval, pyyaml, unicodecsv


## Reading from AWS

You can read from this storage using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='s3://bucket/table.csv')
print(resource.read_rows())
```

For reading from a private bucket you need to setup AWS creadentials as it's described in [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).

## Writing to AWS

> it's not yet supported

## Configuring AWS

There is a control to configure how Frictionless read files in this storage. For example:

```python
from frictionless import Resource
from frictionless.plugins.aws import S3Control

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv', control=controls.S3Control(endpoint_url='<url>'))
```

References:
- [S3 Control](https://frictionlessdata.io/tooling/python/schemes-reference/#s3)