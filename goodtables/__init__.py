# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from . import config
__version__ = config.VERSION


# Module API

from .validate import validate
from .registry import preset
from .registry import check
from .error import Error
from .spec import spec
from .exceptions import GoodtablesException

# Register

import importlib
from . import config
for module in config.PRESETS:
    importlib.import_module(module)
for module in config.CHECKS:
    importlib.import_module(module)

# Deprecated

from . import (exceptions,)
from .cli import (init_datapackage,)
from .inspector import (Inspector,)
