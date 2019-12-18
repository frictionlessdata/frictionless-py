# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from . import config
__version__ = config.VERSION


# Module API

# TODO: somethin wrong goes on with cli here
# The same pattern with `__main__/cli` works fine for tabulator/tableschema/datapackage
# There we don't need to have `__name__ == "__main__":` in cli.py
# And following line doesn't lead to a warning
# from .cli import cli
from .validate import validate
from .registry import preset
from .registry import check
from .error import Error
from .spec import spec
from .exceptions import GoodtablesException

# Deprecated

from . import (exceptions,)
from .helpers import (init_datapackage,)
from .inspector import (Inspector,)

# Register

import importlib
from . import config
for module in config.PRESETS:
    importlib.import_module(module)
for module in config.CHECKS:
    importlib.import_module(module)
