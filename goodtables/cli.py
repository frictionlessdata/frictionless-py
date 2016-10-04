# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import click
from pprint import pformat
from .inspector import Inspector


# Module API

@click.group()
@click.option('--row-limit', type=int)
@click.option('--error-limit', type=int)
@click.pass_context
def cli(ctx, **options):
    ctx.obj['inspector'] = Inspector(**options)


@cli.command()
@click.argument('source')
@click.pass_context
def ckan(ctx, source, **options):
    _report(ctx.obj['inspector'], source, profile='ckan', **options)


@cli.command()
@click.argument('source')
@click.pass_context
def datapackage(ctx, source, **options):
    _report(ctx.obj['inspector'], source, profile='datapackage', **options)


@cli.command()
@click.argument('source')
@click.option('--schema')
@click.pass_context
def table(ctx, source, **options):
    _report(ctx.obj['inspector'], source, profile='table', **options)


# Internal
def _report(inspector, source, profile, **options):
    report = inspector.inspect(source, profile=profile, **options)
    color = 'green' if report['valid'] else 'red'
    tables = report.pop('tables')
    click.secho('REPORT', bold=True)
    click.secho('='*6, bold=True)
    click.secho(pformat(report), fg=color, bold=True)
    for table_number, table in enumerate(tables, start=1):
        click.secho('\nTABLE [%s]' % table_number, bold=True)
        click.secho('='*9, bold=True)
        color = 'green' if table['valid'] else 'red'
        errors = table.pop('errors')
        click.secho(pformat(table), fg=color, bold=True)
        if errors:
            click.secho('-'*9, bold=True)
        for error in errors:
            template = '[{row-number},{col-number}] [{code}] {message}'
            message = template.format(**error)
            click.secho(message)


# Main program

if __name__ == '__main__':
    cli(obj={})
