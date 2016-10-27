# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def preset(name):
    """Register preset.
    """
    def decorator(func):
        func.preset = {
            'name': name,
        }
        return func
    return decorator


def check(error, before=None, after=None):
    """Register check.
    """
    if not isinstance(error, dict):
        error = {'code': error}
    def decorator(func):
        func.check = {
            'error': error,
            'before': before,
            'after': after,
        }
        return func
    return decorator
