from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report1 = inspector.inspect(
    'data/datapackages/valid/datapackage.json', profile='datapackage')
report2 = inspector.inspect(
    'data/datapackages/invalid/datapackage.json', profile='datapackage')
pprint(report1)
pprint(report2)
