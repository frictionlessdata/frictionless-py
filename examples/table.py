from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report1 = inspector.inspect('data/valid.csv')
report2 = inspector.inspect('data/invalid.csv')
pprint(report1)
pprint(report2)
