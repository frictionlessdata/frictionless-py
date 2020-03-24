# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from copy import deepcopy
from goodtables import validate


# Validate

FK_DESCRIPTOR = {
  'resources': [
    {
      'name': 'cities',
      'data': [
        ['id', 'name', 'next_id'],
        [1, 'london', 2],
        [2, 'paris', 3],
        [3, 'rome', 4],
        [4, 'rio', None],
      ],
      'schema': {
        'fields': [
          {'name': 'id', 'type': 'integer'},
          {'name': 'name', 'type': 'string'},
          {'name': 'next_id', 'type': 'integer'},
        ],
        'foreignKeys': [
          {
            'fields': 'next_id',
            'reference': {'resource': '', 'fields': 'id'},
          },
          {
            'fields': 'id',
            'reference': {'resource': 'people', 'fields': 'label'},
          },
        ],
      },
    }, {
      'name': 'people',
      'data': [
        ['label', 'population'],
        [1, 8],
        [2, 2],
        [3, 3],
        [4, 6],
      ],
    },
  ],
}


def test_foreign_key(log):
    descriptor = deepcopy(FK_DESCRIPTOR)
    report = validate(descriptor, checks=['foreign-key'])
    assert log(report) == []


def test_foreign_key_not_defined_foreign_keys(log):
    descriptor = deepcopy(FK_DESCRIPTOR)
    del descriptor['resources'][0]['schema']['foreignKeys']
    report = validate(descriptor, checks=['foreign-key'])
    assert log(report) == []


def test_foreign_key_source_is_not_datapackage(log):
    report = validate('data/valid.csv', checks=['foreign-key'])
    assert log(report) == []


def test_foreign_key_self_referenced_resource_violation(log):
    descriptor = deepcopy(FK_DESCRIPTOR)
    del descriptor['resources'][0]['data'][4]
    report = validate(descriptor, checks=['foreign-key'])
    assert log(report) == [
        (1, 4, 3, 'foreign-key'),
    ]


def test_foreign_key_internal_resource_violation(log):
    descriptor = deepcopy(FK_DESCRIPTOR)
    del descriptor['resources'][1]['data'][4]
    report = validate(descriptor, checks=['foreign-key'])
    assert log(report) == [
        (1, 5, 1, 'foreign-key'),
    ]


def test_foreign_key_internal_resource_violation_non_existent(log):
    descriptor = deepcopy(FK_DESCRIPTOR)
    del descriptor['resources'][1]
    report = validate(descriptor, checks=['foreign-key'])
    assert log(report) == [
        (1, 2, 1, 'foreign-key'),
        (1, 3, 1, 'foreign-key'),
        (1, 4, 1, 'foreign-key'),
        (1, 5, 1, 'foreign-key'),
    ]


def test_foreign_key_external_resource(log):
    descriptor = 'data/datapackages_linked/cities/datapackage.json'
    report = validate(descriptor, checks=['structure', 'schema', 'foreign-key'])
    assert log(report) == []


def test_foreign_key_external_resource_errors(log):
    descriptor = 'data/datapackages_linked_errors/cities/datapackage.json'
    report = validate(descriptor, checks=['structure', 'schema', 'foreign-key'])
    assert log(report) == [
        (1, 4, 1, 'foreign-key'),  # self-referenced
        (1, 4, 3, 'foreign-key'),  # external
    ]


def test_foreign_key_external_resource_remote_datapackage(log):
    descriptor = {
        'resources': [{
          'name': 'countries',
          'data': [
            ['Country Code', 'Country Name'],
            ['PRT', 'Portugal'],
            ['DRL', 'Dreamland'],
          ],
          'schema': {
            'fields': [
              {'name': 'Country Code', 'type': 'string'},
              {'name': 'Country Name', 'type': 'string'},
            ],
            'foreignKeys': [
              {
                'fields': 'Country Code',
                'reference': {'package': 'https://raw.githubusercontent.com/datasets/gdp/master/datapackage.json', 'resource': 'gdp', 'fields': 'Country Code'},
              },
            ],
          },
          }]
    }
    report = validate(descriptor, checks=['structure', 'schema', 'foreign-key'])
    assert log(report) == [
        (1, 3, 1, 'foreign-key'),
    ]
