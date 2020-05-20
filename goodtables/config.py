from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
REPORT_PROFILE = read_asset('profiles', 'report.json')
TASK_PROFILE = read_asset('profiles', 'task.json')
MISSING_VALUES = ['']
