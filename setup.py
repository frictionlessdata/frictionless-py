from setuptools import setup, find_packages


setup(
    name='Tabular Validator',
    version='0.1.1-alpha',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==3.3',
        'jsonschema==2.4.0'
    ],
    dependency_links=[
        'git+https://github.com/okfn/reporter.git#egg=reporter'
    ],
    entry_points={
        'console_scripts': [
            'tv = cli.main:cli',
            ]
    },
)
