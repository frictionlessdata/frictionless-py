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
    'cchardet>=1.0.0',
    'xlrd>=0.9.3',
    'tellme>=0.2.4',
    'jsontableschema>=0.5.1',
    'beautifulsoup4>=4.3.2'
]

setup(
    name='goodtables',
    description='Validate and process tabular data.',
    long_description='Validate and process tabular data.',
    version='0.7.4',
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
            'goodtables = goodtables.cli.main:cli',
        ]
    },
)
