# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import click
import json as json_module
from pprint import pformat
from .inspector import Inspector
click.disable_unicode_literals_warning = True


# Module API

@click.group()
@click.option('--checks')
@click.option('--error-limit', type=int)
@click.option('--table-limit', type=int)
@click.option('--row-limit', type=int)
@click.option('--infer-schema', is_flag=True)
@click.option('--infer-fields', is_flag=True)
@click.option('--order-fields', is_flag=True)
@click.option('--json', is_flag=True)
@click.pass_context
def cli(ctx, json, **options):
    options = {key: value for key, value in options.items() if value is not None}
    ctx.obj = {}
    ctx.obj['inspector'] = Inspector(**options)
    ctx.obj['json'] = json


@cli.command()
@click.argument('source')
@click.pass_context
def datapackage(ctx, source, **options):
    report = ctx.obj['inspector'].inspect(source, preset='datapackage', **options)
    _print_report(report, json=ctx.obj['json'])
    exit(not report['valid'])


@cli.command()
@click.argument('source')
@click.option('--schema')
@click.pass_context
def table(ctx, source, **options):
    report = ctx.obj['inspector'].inspect(source, preset='table', **options)
    _print_report(report, json=ctx.obj['json'])
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
