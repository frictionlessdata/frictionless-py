# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
from setuptools import setup, find_packages


# Helpers
def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


# Prepare
PACKAGE = 'goodtables'
NAME = PACKAGE.replace('_', '-')
INSTALL_REQUIRES = [
    'six>=1.9,<2.0',
    'click>=6.6,<7.0',
    'requests>=2.10,<3.0',
    'tabulator>=1.0.0a5,<2.0',
    # TODO: update after specs-v1
    'jsontableschema>=0.10.1,<1.0',
    'datapackage>=0.8.9,<1.0',
]
INSTALL_FORMAT_ODS_REQUIRES = [
    'ezodf>=0.3,<2.0',
    'lxml>=3.0,<4.0',
]
TESTS_REQUIRE = [
    'pylama',
    'tox',
]
README = read('README.md')
VERSION = read(PACKAGE, 'VERSION')
PACKAGES = find_packages(exclude=['examples', 'tests'])


# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={
        'develop': TESTS_REQUIRE,
        'ods': INSTALL_FORMAT_ODS_REQUIRES,
    },
    entry_points={
        'console_scripts': [
            'goodtables = goodtables.cli:cli',
        ]
    },
    zip_safe=False,
    long_description=README,
    description='Goodtables is a framework to inspect tabular data.',
    author='Open Knowledge International',
    author_email='info@okfn.org',
    url='https://github.com/frictionlessdata/goodtables',
    license='MIT',
    keywords=[
        'data validation',
        'frictionless data',
        'open data',
        'json schema',
        'json table schema',
        'data package',
        'tabular data package',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
