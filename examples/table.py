from pprint import pprint
from goodtables import Inspector, exceptions

inspector = Inspector()
pprint(inspector.inspect('data/valid.csv'))
pprint(inspector.inspect('data/invalid.csv'))
