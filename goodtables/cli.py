# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import click
import goodtables
import json as json_module
from pprint import pformat
click.disable_unicode_literals_warning = True


# Module API

@click.command()
@click.argument('source')
@click.option('--preset')
@click.option('--schema')
@click.option('--checks')
@click.option('--infer-schema', is_flag=True)
@click.option('--infer-fields', is_flag=True)
@click.option('--order-fields', is_flag=True)
@click.option('--error-limit', type=int)
@click.option('--table-limit', type=int)
@click.option('--row-limit', type=int)
@click.option('--json', is_flag=True)
@click.version_option(goodtables.__version__, message='%(version)s')
def cli(source, json, **options):
    """https://github.com/frictionlessdata/goodtables-py#cli
    """
    options = {key: value for key, value in options.items() if value is not None}
    report = goodtables.validate(source, **options)
    _print_report(report, json=json)
    exit(not report['valid'])


# Internal
def _print_report(report, json=False):
    if json:
        return print(json_module.dumps(report, indent=4))
    color = 'green' if report['valid'] else 'red'
    tables = report.pop('tables')
    warnings = report.pop('warnings')
    click.secho('DATASET', bold=True)
    click.secho('='*7, bold=True)
    click.secho(pformat(report), fg=color, bold=True)
    if warnings:
        click.secho('-'*9, bold=True)
    for warning in warnings:
        click.secho('Warning: %s' % warning, fg='yellow')
    for table_number, table in enumerate(tables, start=1):
        click.secho('\nTABLE [%s]' % table_number, bold=True)
        click.secho('='*9, bold=True)
        color = 'green' if table['valid'] else 'red'
        errors = table.pop('errors')
        click.secho(pformat(table), fg=color, bold=True)
        if errors:
            click.secho('-'*9, bold=True)
        for error in errors:
            error = {key: value or '-' for key, value in error.items()}
            template = '[{row-number},{column-number}] [{code}] {message}'
            message = template.format(**error)
            click.secho(message)


# Main program

if __name__ == '__main__':
    cli()
