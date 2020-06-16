import io
import os
import datetime
import itertools
import stringcase
from cached_property import cached_property


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


def apply_function(function, descriptor):
    options = create_options_from_descriptor(descriptor)
    return function(**options)


def create_options_from_descriptor(descriptor):
    return {stringcase.snakecase(key): value for key, value in descriptor.items()}


def create_descriptor_from_options(**options):
    return {stringcase.camelcase(key): value for key, value in options.items()}


def detect_source_type(source):
    source_type = 'table'
    if isinstance(source, dict):
        if source.get('fields') is not None:
            source_type = 'schema'
        if source.get('path') is not None or source.get('data') is not None:
            source_type = 'resource'
        if source.get('resources') is not None:
            source_type = 'package'
        if source.get('tasks') is not None:
            source_type = 'inquiry'
    if isinstance(source, str):
        if source.endswith('schema.json'):
            source_type = 'schema'
        if source.endswith('resource.json'):
            source_type = 'resource'
        if source.endswith('datapackage.json'):
            source_type = 'package'
        if source.endswith('inquiry.json'):
            source_type = 'inquiry'
    return source_type


def reset_cached_properties(obj):
    for name, attr in type(obj).__dict__.items():
        if isinstance(attr, cached_property):
            obj.__dict__.pop(name, None)


# Integrity


def create_lookup(resource, *, package=None):
    lookup = {}
    for fk in resource.schema.foreign_keys:
        source_name = fk['reference']['resource']
        source_key = tuple(fk['reference']['fields'])
        source_res = package.get_resource(source_name) if source_name else resource
        if source_name != '' and not package:
            continue
        lookup.setdefault(source_name, {})
        if source_key in lookup[source_name]:
            continue
        lookup[source_name][source_key] = set()
        if not source_res:
            continue
        try:
            # Current version of tableschema/datapackage raises cast errors
            # In the future this code should use not raising iterator
            for keyed_row in source_res.iter(keyed=True):
                cells = tuple(keyed_row[field_name] for field_name in source_key)
                if set(cells) == {None}:
                    continue
                lookup[source_name][source_key].add(cells)
        except Exception:
            pass
    return lookup


# Compatability


def translate_headers(headers):
    # goodtables: [2, 3, 4] (pandas-like)
    # tabulator: [2, 4] (range-like)
    if headers and isinstance(headers, list):
        if len(headers) == 1:
            return headers[0]
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


def translate_dialect(dialect):
    options = {
        stringcase.lowercase(key): dialect.pop(key)
        for key in [
            'doubleQuote',
            'escapeChar',
            'lineTerminator',
            'quoteChar',
            'skipInitialSpace',
        ]
        if key in dialect
    }
    options.pop('header', None)
    options.pop('caseSensitiveHeader', None)
    options.update(create_options_from_descriptor(dialect))
    return options


def translate_control(control):
    return create_options_from_descriptor(control)


# Measurements


class Timer:
    def __init__(self):
        self.__initial = datetime.datetime.now()

    def get_time(self):
        current = datetime.datetime.now()
        return round((current - self.__initial).total_seconds(), 3)


def get_current_memory_usage():
    # Current memory usage of the current process in MB
    # This will only work on systems with a /proc file system (like Linux)
    # https://stackoverflow.com/questions/897941/python-equivalent-of-phps-memory-get-usage
    try:
        with open('/proc/self/status') as status:
            for line in status:
                parts = line.split()
                key = parts[0][2:-1].lower()
                if key == 'rss':
                    return int(parts[1]) / 1000
    except Exception:
        pass
