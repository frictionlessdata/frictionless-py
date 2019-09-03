# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from datapackage import Package
from ...registry import check
from ...error import Error


# Module API

@check('foreign-keys', type='custom', context='body')
class ForeignKeys(object):

    # Public

    def __init__(self, **options):
        self.__relations = None

    def check_row(self, cells):

        # Get relations
        if self.__relations is None:
            #  self.__relations = self.__get_relations()
            pass

    # Private

    def __get_relations(package, schema):
        # It's based on the following code:
        # https://github.com/frictionlessdata/datapackage-py/blob/master/datapackage/resource.py#L393

        # Prepare resources
        resources = {}
        for fk in schema.foreign_keys:
            resource_name = fk['reference'].get('resource')
            package_name = fk['reference'].get('package')

            # Self-referenced resource
            # TODO: fix usage of undefined self
            if not resource_name:
                resource = self

            # Internal resource
            elif not package_name:
                resource = package.get_resource(resource_name)

            # Check/add resource
            # TODO: don't raise an exception
            if not resource:
                message = 'Foreign key "%s" violation: resource not found'
                message = message % fk['fields']
                raise exceptions.RelationError(message)
            resources[resource_name] = resource

        # Fill relations
        relations = {}
        for resource_name, resource in resources.items():
            if resource.tabular:
                relations[resource_name] = resource.read(keyed=True)

        return relations

    def __resolve_relations(self, row, headers, relations, foreign_key):
        # It's based on the following code:
        # https://github.com/frictionlessdata/tableschema-py/blob/master/tableschema/table.py#L228

        # Prepare helpers - needed data structures
        keyed_row = OrderedDict(zip(headers, row))
        fields = list(zip(foreign_key['fields'], foreign_key['reference']['fields']))
        reference = relations.get(foreign_key['reference']['resource'])
        if not reference:
            return row

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

        return list(keyed_row.values()) if valid else None
