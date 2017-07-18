# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


# Module API

def preset(name):
    """https://github.com/frictionlessdata/goodtables-py#custom-presets
    """
    def decorator(func):
        func.preset = {
            'name': name,
        }
        return func
    return decorator


def check(code, type=None, context=None, before=None, after=None):
    """https://github.com/frictionlessdata/goodtables-py#custom-checks
    """
    def decorator(func):
        func.check = {
            'code': code,
            'type': type,
            'context': context,
            'before': before,
            'after': after,
        }
        return func
    return decorator
