# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from copy import deepcopy
from collections import OrderedDict
from .spec import spec
from . import exceptions


# Module API

def preset(name):
    """https://github.com/frictionlessdata/goodtables-py#custom-presets
    """
    def decorator(func):
        registry.register_preset(func, name)
        return func
    return decorator


def check(name, type, context, position=None):
    """https://github.com/frictionlessdata/goodtables-py#custom-checks
    """
    def decorator(func):
        registry.register_check(func, name, type, context, position)
        return func
    return decorator


class Registry(object):

    # Public

    def __init__(self):
        self.__presets = OrderedDict()
        self.__checks = OrderedDict()

    def register_preset(self, func, name):
        self.__presets[name] = {
            'func': func,
            'name': name,
        }

    def compile_presets(self):
        return deepcopy(self.__presets)

    def register_check(self, func, name, type, context, position=None):
        check = {
            'func': func,
            'name': name,
            'type': type,
            'context': context,
        }

        # Validate check
        error = spec['errors'].get(name)
        if error and (error['type'] != type or error['context'] != context):
            message = 'Check "%s" is a part of the spec but type/context is incorrect'
            raise exceptions.GoodtablesException(message % name)
        elif not error and type != 'custom':
            message = 'Check "%s" is not a part of the spec should have type "custom"'
            raise exceptions.GoodtablesException(message % name)

        # Validate position
        if position:
            try:
                position = position.split(':', 1)
                assert position[0] in ['before', 'after']
                assert self.__checks.get(position[1])
            except (TypeError, AssertionError):
                message = 'Check "%s" has been registered at invalid position "%s"'
                raise exceptions.GoodtablesException(message % (name, position))

        # Insert into checks
        checks = OrderedDict()
        self.__checks.pop(name, None)
        for item_name, item_check in self.__checks.items():
            if position == 'before:%s' % item_name:
                checks[name] = check
            checks[item_name] = item_check
            if position == 'after:%s' % item_name:
                checks[name] = check
        if not position:
            checks[name] = check
        self.__checks = checks

    def compile_checks(self, config, **options):
        config = deepcopy(config)

        # Normalize string config
        if isinstance(config, six.string_types):
            config = [config]

        # Normalize list config
        if isinstance(config, list):
            result = {}
            for item in config:
                if isinstance(item, six.string_types):
                    result[item] = True
                if isinstance(item, dict):
                    result.update(item)
            config = result

        # Validate config
        if not isinstance(config, dict):
            message = 'Checks config "%s" is not valid' % config
            raise exceptions.GoodtablesException(message)

        # Expand config
        for group in ['schema', 'structure', 'spec']:
            for name, value in list(config.items()):
                if name == group:
                    del config[group]
                    for code, error in spec['errors'].items():
                        if group == 'spec' or error['type'] == group:
                            config.setdefault(code, value)

        # Compile checks
        checks = []
        for name, check in deepcopy(self.__checks).items():
            check_config = config.get(name, False)
            if check_config:
                if isinstance(check['func'], type):
                    check_options = deepcopy(options)
                    if isinstance(check_config, dict):
                        check_options.update(check_config)
                    try:
                        check['func'] = check['func'](**check_options)
                    except Exception:
                        message = 'Check "%s" options "%s" error'
                        raise exceptions.GoodtablesException(
                            message, (check['name'], check_options))
                checks.append(check)

        return checks


registry = Registry()
