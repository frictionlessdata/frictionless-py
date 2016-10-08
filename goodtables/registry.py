# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

profiles = {}
checks = {}


def profile(name):
    """Register profile.
    """
    def decorator(func):
        profiles[name] = func
        return func
    return decorator


def check(error):
    """Register check.
    """
    def decorator(func):
        checks[error] = func
        return func
    return decorator


def register_builtin():
    from . import profiles  # noqa
    from . import checks  # noqa
