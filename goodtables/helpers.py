import io
import os


# General


def read_asset(*paths):
    io.open(os.path.join(os.path.dirname(__file__), 'assets', *paths)).read().strip()
