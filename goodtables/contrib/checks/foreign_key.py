# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from datapackage import Package
from ...registry import check
from ...error import Error


# Module API

@check('foreign-key', type='custom', context='body')
class ForeignKey(object):

    # Public

    def __init__(self, **options):
        self.__schema = None
        self.__package = None
        self.__relations = None

    def prepare(self, stream, schema, extra):

        # Prepare schema
        if not schema:
            return False
        if not schema.foreign_keys:
            return False
        self.__schema = schema

        # Prepare package
        if 'datapackage' not in extra:
            return False
        self.__package = Package(json.loads(extra['datapackage']))

        # Prepare relations
        relations = _get_relations(self.__schema, self.__package,
            current_resource_name=extra.get('resource-name'))
        if not relations:
            return False
        self.__relations = relations

        return True

    def check_row(self, cells):

        # Prepare keyed_row
        keyed_row = {}
        for cell in cells:
            if cell.get('header'):
                keyed_row[cell.get('header')] = cell.get('value')

        # Resolve relations
        for foreign_key in self.__schema.foreign_keys:
            keyed_row = _resolve_relations(keyed_row, self.__relations, foreign_key)
            if keyed_row is None:
                # TODO: improve error
                message = 'Foreign Key violation'
                error = Error(
                    'foreign-key',
                    row_number=cells[0]['row-number'],
                    message=message
                )
                return [error]


# Internal

def _get_relations(schema, package, current_resource_name=None):
    # It's based on the following code:
    # https://github.com/frictionlessdata/datapackage-py/blob/master/datapackage/resource.py#L393

    # Prepare resources
    resources = {}
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
        # For now, we rely on uniqueness of resource names and relative paths
        else:
            package = Package('/'.join([package.base_path, package_name]))
            resource = package.get_resource(resource_name)

        # Check/add resource
        # TODO: don't raise an exception
        if not resource:
            message = 'Foreign key "%s" violation: resource not found'
            message = message % fk['fields']
            #  raise exceptions.RelationError(message)
        resources[resource_name] = resource

    # Prepare relations
    relations = {}
    for resource_name, resource in resources.items():
        if resource.tabular:
            relations[resource_name] = resource.read(keyed=True)

    return relations


def _resolve_relations(keyed_row, relations, foreign_key):
    # It's based on the following code:
    # https://github.com/frictionlessdata/tableschema-py/blob/master/tableschema/table.py#L228

    # Prepare helpers - needed data structures
    fields = list(zip(foreign_key['fields'], foreign_key['reference']['fields']))
    reference = relations.get(foreign_key['reference']['resource'])
    if not reference:
        return keyed_row

    # Collect values - valid if all None
    values = {}
    valid = True
    for field, ref_field in fields:
        if field and ref_field:
            values[ref_field] = keyed_row[field]
            if keyed_row[field] is not None:
                valid = False

    # Resolve values - valid if match found
    if not valid:
        for refValues in reference:
            if set(values.items()).issubset(set(refValues.items())):
                for field, ref_field in fields:
                    keyed_row[field] = refValues
                valid = True
                break

    return keyed_row if valid else None
