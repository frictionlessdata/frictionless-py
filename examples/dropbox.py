import dropbox
from pprint import pprint
from tabulator import Stream
from goodtables import Inspector, preset

# 1. Create app to generate access token at https://www.dropbox.com/developers/apps
# 2. And add some csv files to FOLDER on dropbox
ACCESS_TOKEN = '<insert-access-token>'
FOLDER = '/goodtables'

# Get dropbox client
client = dropbox.dropbox.Dropbox(ACCESS_TOKEN)

@preset('dropbox')
def dropbox_preset(source, **options):
    warnings = []
    tables = []
    for item in client.files_list_folder(source).entries:
        if item.path_lower.endswith('.csv'):
            url = client.files_get_temporary_link(item.path_lower).link
            tables.append({
                'source': url,
                'stream': Stream(url, headers=1, format='csv'),
                'schema': None,
                'extra': {
                    'folder': source,
                },
            })
    return warnings, tables

inspector = Inspector(custom_presets=[dropbox_preset])
report = inspector.inspect(FOLDER, preset='dropbox')
pprint(report)
