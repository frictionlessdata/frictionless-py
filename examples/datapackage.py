from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report1 = inspector.inspect(
    'data/datapackages/valid/datapackage.json', preset='datapackage')
report2 = inspector.inspect(
    'data/datapackages/invalid/datapackage.json', preset='datapackage')
pprint(report1)
pprint(report2)
