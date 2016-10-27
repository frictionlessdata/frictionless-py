import os
from pprint import pprint
from jsontableschema import Table
from goodtables import Inspector, preset

@preset('csvdir')
def csvdir(errors, tables, source):
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if name.endswith('.csv'):
            tables.append({
                'table': Table(path),
                'extra': {'filename': name},
            })


inspector = Inspector(custom_presets=[csvdir])
report = inspector.inspect('data', preset='csvdir')
pprint(report)
