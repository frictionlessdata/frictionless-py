import json
from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
JOB_PROFILE = json.loads(read_asset('profiles', 'job.json'))
REPORT_PROFILE = json.loads(read_asset('profiles', 'report.json'))
REMOTE_SCHEMES = ['http', 'https', 'ftp', 'ftps']
MISSING_VALUES = ['']
