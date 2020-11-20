# Working with Filelike Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1iC0rS6Q80D6lS7Pi6k65bCU5ytNhTtyZ)



> Status: **CORE / STABLE**


```bash
!pip install frictionless
```


```bash
! wget -q -O table.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv
! cat table.csv
```

    id,name
    1,english
    2,中国人


## Reading Filelike Data


You can read Filelike using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

with open('table.csv', 'rb') as file:
  resource = Resource(path=file, format='csv')
  print(resource.read_rows())
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-4-5489884a036d> in <module>()
          3 with open('table.csv', 'rb') as file:
          4   resource = Resource(path=file, format='csv')
    ----> 5   print(resource.read_rows())


    /usr/local/lib/python3.6/dist-packages/frictionless/resource.py in read_rows(self)
        535             Row[]: resource rows
        536         """
    --> 537         rows = list(self.read_row_stream())
        538         return rows
        539


    /usr/local/lib/python3.6/dist-packages/frictionless/resource.py in read_row_stream(self)
        543             gen<Row[]>: row stream
        544         """
    --> 545         with self.to_table() as table:
        546             for row in table.row_stream:
        547                 yield row


    /usr/local/lib/python3.6/dist-packages/frictionless/table.py in __enter__(self)
        205     def __enter__(self):
        206         if self.closed:
    --> 207             self.open()
        208         return self
        209


    /usr/local/lib/python3.6/dist-packages/frictionless/table.py in open(self)
        390             self.__resource.stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        391             self.__parser = system.create_parser(self.__resource)
    --> 392             self.__parser.open()
        393             self.__data_stream = self.__read_data_stream()
        394             self.__row_stream = self.__read_row_stream()


    /usr/local/lib/python3.6/dist-packages/frictionless/parser.py in open(self)
         70             raise exceptions.FrictionlessException(error)
         71         try:
    ---> 72             self.__loader = self.read_loader()
         73             self.__data_stream = self.read_data_stream()
         74             return self


    /usr/local/lib/python3.6/dist-packages/frictionless/parser.py in read_loader(self)
        101         if self.loading:
        102             loader = system.create_loader(self.resource)
    --> 103             return loader.open()
        104
        105     def read_data_stream(self):


    /usr/local/lib/python3.6/dist-packages/frictionless/loader.py in open(self)
         79             raise exceptions.FrictionlessException(error)
         80         try:
    ---> 81             self.__byte_stream = self.read_byte_stream()
         82             return self
         83         except Exception:


    /usr/local/lib/python3.6/dist-packages/frictionless/loader.py in read_byte_stream(self)
        109         """
        110         try:
    --> 111             byte_stream = self.read_byte_stream_create()
        112             byte_stream = self.read_byte_stream_infer_stats(byte_stream)
        113             byte_stream = self.read_byte_stream_decompress(byte_stream)


    /usr/local/lib/python3.6/dist-packages/frictionless/loaders/local.py in read_byte_stream_create(self)
         17         scheme = "file://"
         18         source = self.resource.source
    ---> 19         if source.startswith(scheme):
         20             source = source.replace(scheme, "", 1)
         21         byte_stream = io.open(source, "rb")


    AttributeError: 'list' object has no attribute 'startswith'


## Writing Filelike Data

The same is actual for writing CSV:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv')
```


```bash
!cat table.new.csv
```

## Configuring Filelike Data
