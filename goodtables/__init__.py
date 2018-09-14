# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import importlib
import importlib.util
import io
import json
import os

from . import config, exceptions
from .error import Error
from .inspector import Inspector
from .registry import Registry, check, preset
from .validate import init_datapackage, validate

# Module API


# Version

__version__ = io.open(
    os.path.join(os.path.dirname(__file__), 'VERSION'),
    encoding='utf-8').read().strip()

# Init functions


def init(spec_path=None):
    """ First method to call before using module """

    # Load errors specifications
    spec = load_spec(spec_path)

    # Inits Error class
    Error.init(spec)

    # Inits Registry class before loading files using @preset or/and @check
    Registry.init(spec)

    # Load presets and core checks
    for module in config.PRESETS:
        importlib.import_module(module)
    for module in config.CHECKS:
        importlib.import_module(module)


def load_spec(path=None):
    """ Loads spec configuration from given path or project spec.json if no given path """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'spec.json')
    spec = json.load(io.open(path, encoding='utf-8'))
    return spec


# Handy functions to load additional external user-defined custom checks


def load_check_from_module(path):
    """
        Loads a custom checks module from python script path
        Module name is filename (without .py extension)
    """
    module_name = os.path.splitext(os.path.basename(path))[0]
    module_spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)


def load_checks_from_dir(checks_dir):
    """ Loads custom modules from py files in the given dir """
    for name in os.listdir(checks_dir):
        if not name.endswith('.py') or name == '__init__.py':
            continue
        path = os.path.join(checks_dir, name)
        load_check_from_module(path)
