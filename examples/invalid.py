from pprint import pprint
from goodtables import Inspector, exceptions

inspector = Inspector()
pprint(inspector.inspect({'source': 'data/invalid.csv'}))
