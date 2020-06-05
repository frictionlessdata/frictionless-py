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
CORE_REQUIRES = [
    'six>=1.9',
    'click>=6.6',
    'click-default-group',
    'cached-property>=1.5',
    'stringcase>=1.2',
    'requests>=2.10',
    'jsonschema>=2.5',
    'tabulator>=1.51',
    'tableschema>=1.19',
    'datapackage>=1.14',
]
GUESS_REQUIRES = [
    'statistics>=1.0',
]
RULE_REQUIRES = [
    'simpleeval>=0.9',
]
SERVER_REQUIRES = [
    'gunicorn>=20',
]
DEVOPS_REQUIRES = [
    'mypy',
    'black',
    'pylama',
    'pytest',
    'pytest-cov',
    'coveralls',
    'ipython',
]
README = read('README.md')
VERSION = read(PACKAGE, 'assets', 'VERSION')
PACKAGES = find_packages(exclude=['tests'])
ENTRY_POINTS = {'console_scripts': ['goodtables = goodtables.__main__:cli']}


# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=CORE_REQUIRES,
    tests_require=DEVOPS_REQUIRES,
    extras_require={
        'guess': GUESS_REQUIRES,
        'rule': RULE_REQUIRES,
        'server': SERVER_REQUIRES,
        'devops': DEVOPS_REQUIRES,
    },
    entry_points=ENTRY_POINTS,
    zip_safe=False,
    long_description=README,
    long_description_content_type='text/markdown',
    description='Goodtables is a framework for tabular data validation',
    author='Open Knowledge Foundation',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
