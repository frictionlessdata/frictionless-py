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

        # Prepare relations
        self.__relations = _get_relations(
            self.__package, self.__schema,
            current_resource_name=extra['resource-name'])

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
            success = _resolve_relations(keyed_row, foreign_key, relations=self.__relations)
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
        # For now, we rely on uniqueness of resource names and relative paths
        else:
            package = Package('/'.join([package.base_path, package_name]))
            resource = package.get_resource(resource_name)

        # Add to relations (can be None)
        relations[resource_name] = resource
        if resource and resource.tabular:
            relations[resource_name] = resource.read(keyed=True)

    return relations


def _resolve_relations(keyed_row, foreign_key, relations=None):
    # It's based on the following code:
    # https://github.com/frictionlessdata/tableschema-py/blob/master/tableschema/table.py#L228

    # Prepare helpers - needed data structures
    fields = list(zip(foreign_key['fields'], foreign_key['reference']['fields']))
    reference = relations.get(foreign_key['reference']['resource'])
    if not reference:
        return None

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
