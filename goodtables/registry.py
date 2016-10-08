# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import six
import json
import datetime
from . import exceptions


# Module API

profiles = {}
checks = {}
errors = []


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
        # Check for buitin error
        if isinstance(error, six.string_types):
            checks[error] = func
        # Check for custom error
        else:
            checks[error['code']] = func
            mapping = {error: index for index, error in enumerate(errors)}
            if error['before'] in mapping:
                errors.insert(mapping[errors['before']], error)
            elif error['after'] in mapping:
                errors.insert(mapping[errors['after']] + 1, error)
        return func
    return decorator


def register_builtin():

    # Register errors
    base = os.path.dirname(__file__)
    path = os.path.join(base, 'spec.json')
    spec = json.load(io.open(path, encoding='utf-8'))
    errors.extend(spec['errors'])

    # Register profiles/checks
    from . import profiles  # noqa
    from . import checks  # noqa
