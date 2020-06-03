import io
import os
import datetime
import itertools


# General


def read_asset(*paths):
    dirname = os.path.dirname(__file__)
    return io.open(os.path.join(dirname, 'assets', *paths)).read().strip()


def combine(*iterators):
    combine.missing = '__combine_missing__'
    return itertools.zip_longest(*iterators, fillvalue=combine.missing)


def find_positions(haystack, needle):
    positions = []
    for position, value in enumerate(haystack, start=1):
        if value == needle:
            positions.append(position)
    return positions


def parse_hashing_algorithm(hash):
    if not hash:
        return 'md5'
    parts = hash.split(':', maxsplit=1)
    return parts[0] if len(parts) > 1 else 'md5'


def parse_hashing_digest(hash):
    if not hash:
        return ''
    parts = hash.split(':', maxsplit=1)
    return parts[1] if len(parts) > 1 else hash


# Compatability


def translate_headers(headers):
    # goodtables: [2, 3, 4] (pandas-like)
    # tabulator: [2, 4] (range-like)
    if headers and isinstance(headers, list):
        if len(headers) > 1:
            headers = [headers[0], headers[-1]]
            for header in headers:
                assert isinstance(header, int)
    return headers


def translate_pick_fields(pick_fields):
    for index, item in enumerate(pick_fields or []):
        if isinstance(item, str) and item.startswith('<regex>'):
            pick_fields[index] = {'type': 'regex', 'value': item.replace('<regex>', '')}
    return pick_fields


def translate_skip_fields(skip_fields):
    for index, item in enumerate(skip_fields or []):
        if isinstance(item, str) and item.startswith('<regex>'):
            skip_fields[index] = {'type': 'regex', 'value': item.replace('<regex>', '')}
    return skip_fields


def translate_pick_rows(pick_rows):
    for index, item in enumerate(pick_rows or []):
        if isinstance(item, str) and item.startswith('<regex>'):
            pick_rows[index] = {'type': 'regex', 'value': item.replace('<regex>', '')}
    return pick_rows


def translate_skip_rows(skip_rows):
    for index, item in enumerate(skip_rows or []):
        if isinstance(item, str) and item.startswith('<regex>'):
            skip_rows[index] = {'type': 'regex', 'value': item.replace('<regex>', '')}
        if isinstance(item, str) and item.startswith('<blank>'):
            skip_rows[index] = {'type': 'preset', 'value': 'blank'}
    return skip_rows


# Measurements


class Timer:
    def __init__(self):
        self.__initial = datetime.datetime.now()

    def get_time(self):
        current = datetime.datetime.now()
        return round((current - self.__initial).total_seconds(), 3)
