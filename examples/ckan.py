from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
report = inspector.inspect('http://data.surrey.ca', profile='ckan')
pprint(report)
