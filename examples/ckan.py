from pprint import pprint
from goodtables import Inspector

inspector = Inspector()
pprint(inspector.inspect('http://data.surrey.ca', profile='ckan'))
