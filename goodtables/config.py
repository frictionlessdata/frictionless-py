from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
REPORT_PROFILE = read_asset('profiles', 'report.json')
MISSING_VALUES = ['']
