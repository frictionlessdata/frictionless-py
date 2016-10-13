import os
from pprint import pprint
from jsontableschema import Table
from goodtables import Inspector, profile

@profile('csvdir')
def csvdir(errors, tables, source):
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if name.endswith('.csv'):
            tables.append({
                'table': Table(path),
                'extra': {'filename': name},
            })


inspector = Inspector(custom_profiles=[csvdir])
report = inspector.inspect('data', profile='csvdir')
pprint(report)
