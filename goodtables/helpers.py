import io
import os
import datetime
import itertools


# General


def read_asset(*paths):
    io.open(os.path.join(os.path.dirname(__file__), 'assets', *paths)).read().strip()


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


# Measurements


class Timer:
    def __init__(self):
        self.__initial = datetime.datetime.now()

    def get_time(self):
        current = datetime.datetime.now()
        return round((current - self.__initial).total_seconds(), 3)
