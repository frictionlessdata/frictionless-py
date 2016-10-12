from pprint import pprint
from goodtables import Inspector, exceptions

inspector = Inspector()
pprint(inspector.inspect(
    'data/datapackages/valid/datapackage.json', profile='datapackage'))
