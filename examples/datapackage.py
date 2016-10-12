from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect('data/datapackages/valid/datapackage.json', profile='datapackage')
pprint(report)
