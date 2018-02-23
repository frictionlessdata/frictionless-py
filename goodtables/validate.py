# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import datapackage
from .inspector import Inspector


# Module API

def validate(source, **options):
    """Validates a source file and returns a report.

    Args:
        source (Union[str, Dict, List[Dict], IO]): The source to be validated.
            It can be a local file path, URL, dict, list of dicts, or a
            file-like object. If it's a list of dicts and the `preset` is
            "nested", each of the dict key's will be used as if it was passed
            as a keyword argument to this method.

            The file can be a CSV, XLS, JSON, and any other format supported by
            `tabulator`_.

    Keyword Args:
        checks (List[str]): List of checks names to be enabled. They can be
            individual check names (e.g. `blank-headers`), or check types (e.g.
            `structure`).
        skip_checks (List[str]): List of checks names to be skipped. They can
            be individual check names (e.g. `blank-headers`), or check types
            (e.g.  `structure`).
        infer_schema (bool): Infer schema if one wasn't passed as an argument.
        infer_fields (bool): Infer schema for columns not present in the received schema.
        order_fields (bool): Order source columns based on schema fields order.
            This is useful when you don't want to validate that the data
            columns' order is the same as the schema's.
        error_limit (int): Stop validation if the number of errors per table
            exceeds this value.
        table_limit (int): Maximum number of tables to validate.
        row_limit (int): Maximum number of rows to validate.

        preset (str): Dataset type could be `table` (default), `datapackage`,
            `nested` or custom. Usually, the preset can be inferred from the
            source, so you don't need to define it.
        Any (Any): Any additional arguments not defined here will be passed on,
            depending on the chosen `preset`. If the `preset` is `table`, the
            extra arguments will be passed on to `tabulator`_, if it is
            `datapackage`, they will be passed on to the `datapackage`_
            constructor.

        # Table preset
        schema (Union[str, Dict, IO]): The Table Schema for the
            source.
        headers (Union[int, List[str]): Either the row number that contains
            the headers, or a list with them. If the row number is given, ?????
        scheme (str): The scheme used to access the source (e.g. `file`,
            `http`). This is usually inferred correctly from the source. See
            the `tabulator`_ documentation for the list of supported schemes.
        format (str): Format of the source data (`csv`, `datapackage`, ...).
            This is usually inferred correctly from the source. See the
            the `tabulator`_ documentation for the list of supported formats.
        encoding (str): Encoding of the source.
        skip_rows (Union[int, List[Union[int, str]]]): Row numbers or a
            string. Rows beginning with the string will be ignored (e.g. '#',
            '//').

    Raises:
        GoodtablesException: Raised on any non-tabular error.

    Returns:
        dict: The validation report.

    .. _tabulator:
        https://github.com/frictionlessdata/tabulator-py
    .. _tabulator_schemes:
        https://github.com/frictionlessdata/tabulator-py
    .. _tabulator:
        https://github.com/frictionlessdata/datapackage-py
    """
    source, options, inspector_settings = _parse_arguments(source, **options)

    # Validate
    inspector = Inspector(**inspector_settings)
    report = inspector.inspect(source, **options)

    return report


def init_datapackage(resource_paths):
    """Create tabular data package with resources.

    It will also infer the tabular resources' schemas.

    Args:
        resource_paths (List[str]): Paths to the data package resources.

    Returns:
        datapackage.Package: The data package.
    """
    dp = datapackage.Package({
        'name': 'change-me',
        'schema': 'tabular-data-package',
    })

    for path in resource_paths:
        dp.infer(path)

    return dp


def _parse_arguments(source, **options):
    # Extract settings
    validation_options = set((
        'checks',
        'skip_checks',
        'infer_schema',
        'infer_fields',
        'order_fields',
        'error_limit',
        'table_limit',
        'row_limit',
        'custom_presets',
        'custom_checks',
    ))
    settings = dict((
        (key, options.pop(key)) for key in validation_options
        if key in options
    ))

    # Support for pathlib.Path
    if hasattr(source, 'joinpath'):
        source = str(source)
    if isinstance(source, list):
        if source and isinstance(source[0], dict) and 'source' in source[0]:
            for index, item in enumerate(source):
                if hasattr(item['source'], 'joinpath'):
                    source[index]['source'] = str(item['source'])

    return source, options, settings
