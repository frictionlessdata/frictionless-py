from .helpers import read_asset


# General

VERSION = read_asset('VERSION')
SPEC = read_asset('spec.json')
SPEC_PROFILE = read_asset('profiles', 'spec.json')
REPORT_PROFILE = read_asset('profiles', 'report.json')
MISSING_VALUES = ['']
