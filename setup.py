# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import io
from setuptools import setup, find_packages


_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)

dependencies = [
    'Click>=3.3',
    'jsonschema>=2.4.0',
    'tellme>=0.1.2'
]

with io.open('README.md', mode='r+t', encoding='utf-8') as stream:
    readme = stream.read()

setup(
    name='tabular-validator',
    description='A toolkit for validating tabular data through a validation pipeline.',
    long_description=readme,
    version='0.1.0',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://okfn.org',
    license='MIT',
    packages=find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'tv = tabular_validator.cli.main:cli',
        ]
    },
)
