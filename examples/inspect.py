from pprint import pprint
from goodtables import Inspector, exceptions

inspector = Inspector()

# Table
print('Profile [table]:')
pprint(inspector.inspect('data/valid.csv'))
pprint(inspector.inspect('data/invalid.csv'))

# Datapackage
print('\nProfile [datapackage]:')
pprint(inspector.inspect(
    'data/datapackages/valid/datapackage.json', profile='datapackage'))

# Ckan
print('\nProfile [ckan]:')
pprint(inspector.inspect('http://data.surrey.ca', profile='ckan'))
