import dropbox
from pprint import pprint
from tabulator import Stream
from goodtables import Inspector, preset

# Create app to get key and secret at
# https://www.dropbox.com/developers/apps
# And add some csv files to FOLDER on dropbox
APP_KEY = '<insert-app-key>'
APP_SECRET = '<insert-app-secret>'
FOLDER = '/goodtables'

# Authorize clients
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
authorize_url = flow.start()
print('1. Go to: ' + authorize_url)
print('2. Click "Allow" (you might have to log in first)')
print('3. Copy the authorization code.')
code = input("Enter the authorization code here: ").strip()
access_token, user_id = flow.finish(code)
client1 = dropbox.dropbox.Dropbox(access_token)
client2 = dropbox.client.DropboxClient(access_token)

@preset('dropbox')
def dropbox_preset(source, **options):
    errors = []
    tables = []
    for item in client2.metadata(source)['contents']:
        if item['path'].endswith('.csv'):
            url = client1.files_get_temporary_link(item['path']).link
            tables.append({
                'source': url,
                'stream': Stream(url, headers=1, format='csv'),
                'schema': None,
                'extra': {
                    'folder': source,
                },
            })
    return errors, tables

inspector = Inspector(custom_presets=[dropbox_preset])
report = inspector.inspect(FOLDER, preset='dropbox')
pprint(report)
