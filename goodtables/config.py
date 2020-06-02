import json
from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
QUERY_PROFILE = json.loads(read_asset('profiles', 'query.json'))
REPORT_PROFILE = json.loads(read_asset('profiles', 'report.json'))
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']
MISSING_VALUES = ['']
