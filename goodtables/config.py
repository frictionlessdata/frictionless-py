import json
from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
REPORT_PROFILE = json.loads(read_asset('profiles', 'report.json'))
TASK_PROFILE = json.loads(read_asset('profiles', 'task.json'))
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']
MISSING_VALUES = ['']
