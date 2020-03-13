# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import warnings
from copy import deepcopy
from collections import OrderedDict
from .spec import spec
from . import exceptions


# Module API

def preset(name):
    """Register a custom preset (decorator)

    # Example

    ```python
    @preset('custom-preset')
    def custom_preset(source, **options):
        # ...
    ```

    # Arguments
        name (str): preset name

    """
    def decorator(func):
        registry.register_preset(func, name)
        return func
    return decorator


def check(name, type=None, context=None, position=None):
    """Register a custom check (decorator)

    # Example

    ```python
    @check('custom-check', type='custom', context='body')
    def custom_check(cells):
        # ...
    ```

    # Arguments
        name (str): preset name
        type (str): has to be `custom`
        context (str): has to be `head` or `body`
        position (str): has to be `before:<check-name>` or `after:<check-name>`

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

    def register_check(self, func, name, type=None, context=None, position=None):
        check = {
            'func': func,
            'name': name,
            'type': type,
            'context': context,
        }

        # Validate check
        error = spec['errors'].get(name)
        if error:
            if (check['type'] is not None or check['context'] is not None):
                message = 'Check "%s" is a part of the spec but type/context is incorrect'
                raise exceptions.GoodtablesException(message % name)
            check['type'] = error['type']
            check['context'] = error['context']
        elif not error and type != 'custom':
            message = 'Check "%s" is not a part of the spec should have type "custom"'
            raise exceptions.GoodtablesException(message % name)

        # Validate position
        if position:
            try:
                position_args = position.split(':', 1)
                assert position_args[0] in ['before', 'after']
                assert self.__checks.get(position_args[1])
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

    def compile_checks(self, include, exclude, **options):
        include = deepcopy(include)
        exclude = deepcopy(exclude)

        # Deprecated string checks
        if isinstance(include, six.string_types):
            warnings.warn(
                'Checks parameter as a string is deprecated. '
                'Please use a list',
                UserWarning)
            include = [include]

        # Deprecated dict checks
        if isinstance(include, dict):
            warnings.warn(
                'Checks parameter as a dict is deprecated. '
                'Please use a list',
                UserWarning)
            result_include = set()
            result_exclude = set()
            for name, enabled in include.items():
                if enabled:
                    result_include.add(name)
                else:
                    result_include.add('structure')
                    result_include.add('schema')
                    result_exclude.add(name)
            include = list(result_include)
            exclude = list(result_exclude)

        # Validate checks
        if not isinstance(include, (list, tuple)):
            message = 'Checks parameter "%s" is not valid' % include
            raise exceptions.GoodtablesException(message)

        # Expand checks
        for group in ['structure', 'schema']:
            for index, item in enumerate(list(include)):
                if item == group:
                    del include[index]
                    for code, error in spec['errors'].items():
                        # It's temporal skip
                        # https://github.com/frictionlessdata/goodtables-py/issues/174
                        if code == 'schema-error':
                            continue
                        if error['type'] == group:
                            include.append(code)

        # Compile checks
        compiled_checks = []
        for name, check in self.__checks.items():
            if name not in exclude:
                for item in include:
                    item_name = item
                    item_config = {}
                    if isinstance(item, dict):
                        item_name = list(item.keys())[0]
                        item_config = list(item.values())[0]
                    if item_name not in self.__checks:
                        message = 'Check "%s" is not registered'
                        raise exceptions.GoodtablesException(message % item_name)
                    if item_name == name:
                        compiled_check = deepcopy(check)
                        if isinstance(check['func'], type):
                            check_options = deepcopy(options)
                            check_options.update(item_config)
                            try:
                                compiled_check['func'] = check['func'](**check_options)
                            except Exception as e:
                                message = 'Check "%s" options "%s" error'
                                message = message % (check['name'], check_options)
                                six.raise_from(exceptions.GoodtablesException(message), e)
                        compiled_checks.append(compiled_check)

        return compiled_checks


registry = Registry()
