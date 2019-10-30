# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from copy import deepcopy
from collections import defaultdict
from datapackage import Package
from ...registry import check
from ...error import Error


# Module API

@check('foreign-key', type='custom', context='body')
class ForeignKey(object):

    # Public

    def __init__(self, **options):
        self.__package = None
        self.__schema = None
        self.__relations = None
        self.__code = 'foreign-key'

    def prepare(self, stream, schema, extra):

        # Prepare package
        if 'datapackage' not in extra or 'resource-name' not in extra:
            return False
        descriptor = extra['datapackage']
        if descriptor.strip().startswith('{'):
            descriptor = json.loads(descriptor)
        self.__package = Package(descriptor)

        # Prepare schema
        if not schema:
            return False
        if not schema.foreign_keys:
            return False
        self.__schema = schema

        # Prepare foreign keys values
        relations = _get_relations(
            self.__package, self.__schema,
            current_resource_name=extra['resource-name'])
        self.__foreign_keys_values = _get_foreign_keys_values(
            self.__schema, relations)

        return True

    def check_row(self, cells):
        row_number = cells[0]['row-number']

        # Prepare keyed_row
        keyed_row = {}
        for cell in cells:
            if cell.get('field'):
                keyed_row[cell.get('field').name] = cell.get('value')

        # Resolve relations
        errors = []
        for foreign_key in self.__schema.foreign_keys:
            success = _resolve_relations(
                deepcopy(keyed_row), self.__foreign_keys_values, foreign_key)
            if success is None:
                message = 'Foreign key "{fields}" violation in row {row_number}'
                message_substitutions = {'fields': foreign_key['fields']}
                errors.append(Error(
                    self.__code,
                    row_number=row_number,
                    message=message,
                    message_substitutions=message_substitutions,
                ))

        return errors


# Internal

def _get_relations(package, schema, current_resource_name=None):
    # It's based on the following code:
    # https://github.com/frictionlessdata/datapackage-py/blob/master/datapackage/resource.py#L393

    # Prepare relations
    relations = {}
    for fk in schema.foreign_keys:
        resource_name = fk['reference'].get('resource')
        package_name = fk['reference'].get('package')
        resource = None

        # Self-referenced resource
        if not resource_name:
            for item in package.resources:
                if item.name == current_resource_name:
                    resource = item

        # Internal resource
        elif not package_name:
            resource = package.get_resource(resource_name)

        # External resource (experimental)
        # For now, we rely on uniqueness of resource names and support relative paths
        else:
            descriptor = package_name
            if not descriptor.startswith('http'):
                descriptor = '/'.join([package.base_path, package_name])
            package = Package(descriptor)
            resource = package.get_resource(resource_name)

        # Add to relations (can be None)
        relations[resource_name] = resource
        if resource and resource.tabular:
            relations[resource_name] = resource.read(keyed=True)

    return relations


def _get_foreign_keys_values(schema, relations):
    # It's based on the following code:
    # https://github.com/frictionlessdata/tableschema-py/blob/master/tableschema/table.py#L218

    # we dont need to load the complete reference table to test relations
    # we can lower payload AND optimize testing foreign keys
    # by preparing the right index based on the foreign key definition
    # foreign_keys are sets of tuples of all possible values in the foreign table
    # foreign keys =
    # [reference] [foreign_keys tuple] = { (foreign_keys_values, ) : one_keyedrow, ... }
    foreign_keys = defaultdict(dict)
    if schema:
        for fk in schema.foreign_keys:
            # load relation data
            relation = fk['reference']['resource']

            # create a set of foreign keys
            # to optimize we prepare index of existing values
            # this index should use reference + foreign_keys as key
            # cause many foreign keys may use the same reference
            foreign_keys[relation][tuple(fk['reference']['fields'])] = {}
            for row in (relations[relation] or []):
                key = tuple([row[foreign_field] for foreign_field in fk['reference']['fields']])
                # here we should chose to pick the first or nth row which match
                # previous implementation picked the first, so be it
                if key not in foreign_keys[relation][tuple(fk['reference']['fields'])]:
                    foreign_keys[relation][tuple(fk['reference']['fields'])][key] = row
    return foreign_keys


def _resolve_relations(keyed_row, foreign_keys_values, foreign_key):
    # It's based on the following code:
    # https://github.com/frictionlessdata/tableschema-py/blob/master/tableschema/table.py#L228

    # local values of the FK
    local_values = tuple(keyed_row[f] for f in foreign_key['fields'])
    if len([l for l in local_values if l]) > 0:
        # test existence into the foreign
        relation = foreign_key['reference']['resource']
        keys = tuple(foreign_key['reference']['fields'])
        foreign_values = foreign_keys_values[relation][keys]
        if local_values in foreign_values:
            return foreign_values[local_values]
        else:
            return None
    else:
        # empty values for all keys, return original values
        return keyed_row
