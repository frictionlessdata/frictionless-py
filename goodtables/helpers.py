import io
import os
import itertools
import datetime


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


def create_timer():
    def finish(self):
        self.__finish = datetime.datetime.now()
        time = (round((self.__finish - self.__start).total_seconds(), 3),)

    return finish

