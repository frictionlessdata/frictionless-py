import os
from pprint import pprint
from tabulator import Stream
from jsontableschema import Schema
from goodtables import Inspector, preset

@preset('csvdir')
def csvdir(source):
    errors = []
    tables = []
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if name.endswith('.csv'):
            tables.append({
                'source': path,
                'stream': Stream(path, headers=1),
                'schema': None,
                'extra': {
                    'filename': name,
                },
            })
    return errors, tables


inspector = Inspector(custom_presets=[csvdir])
report = inspector.inspect('data', preset='csvdir')
pprint(report)
