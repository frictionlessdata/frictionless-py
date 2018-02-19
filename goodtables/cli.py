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
@click.argument('source', type=click.Path(), nargs=-1, required=True)
@click.option(
    '--init',
    is_flag=True,
    help=(
        'Create data package with the data files received as parameters.'
        ' It will infer the schemas from the data.'
    )
)
@click.option('--quiet', '-q', is_flag=True, help='Don\'t output anything.')
@click.option('--json', is_flag=True, help='Output report as JSON.')
@click.option(
    '--output',
    '-o',
    type=click.File('w'),
    default='-',
    help='Redirect output to a file.'
)
@click.option('--preset')
@click.option('--schema', type=click.Path(), help='Path to a Table Schema.')
@click.option(
    '--infer-schema/--no-infer-schema',
    default=False,
    help='Infer schema. If an explicit schema is defined, infer missing columns only.'
)
@click.option('--checks', '-c', multiple=True, help='Checks to enable.')
@click.option(
    '--skip-checks',
    '-C',
    multiple=True,
    help='Checks to disable.'
)
@click.option(
    '--order-fields',
    is_flag=True,
    help='Don\'t validate the columns order.'
)
@click.option(
    '--row-limit',
    type=int,
    default=-1,
    help='Maximum number of rows to validate (-1 for no limit)'
)
@click.option(
    '--table-limit',
    type=int,
    default=-1,
    help='Maximum number of tables to validate (-1 for no limit)'
)
@click.option(
    '--error-limit',
    type=int,
    default=-1,
    help='Stop validating if there are more than this number of errors (-1 for no limit).'
)
@click.version_option(goodtables.__version__, message='%(version)s')
def cli(source, json, **options):
    # Remove blank values
    options = {key: value for key, value in options.items() if value is not None}
    if not options['checks']:
        del options['checks']
    if not options['skip_checks']:
        del options['skip_checks']

    options['infer_fields'] = options['infer_schema']
    quiet = options.pop('quiet')
    output = options.pop('output')

    sources = [{'source': source} for source in source]

    if options.pop('init'):
        dp = goodtables.init_datapackage(sources, **options)
        print(json_module.dumps(dp.descriptor, indent=4))
        exit(dp.valid)  # Just to be defensive, as it should always be valid.
    else:
        report = goodtables.validate(sources, **options)

        if not quiet:
            _print_report(report, output=output, json=json)

        exit(not report['valid'])


# Internal
def _print_report(report, output=None, json=False):
    def secho(*args, **kwargs):
        click.secho(file=output, *args, **kwargs)

    if json:
        return secho(json_module.dumps(report, indent=4))

    color = 'green' if report['valid'] else 'red'
    tables = report.pop('tables')
    warnings = report.pop('warnings')
    secho('DATASET', bold=True)
    secho('='*7, bold=True)
    secho(pformat(report), fg=color, bold=True)
    if warnings:
        secho('-'*9, bold=True)
    for warning in warnings:
        secho('Warning: %s' % warning, fg='yellow')
    for table_number, table in enumerate(tables, start=1):
        secho('\nTABLE [%s]' % table_number, bold=True)
        secho('='*9, bold=True)
        color = 'green' if table['valid'] else 'red'
        errors = table.pop('errors')
        secho(pformat(table), fg=color, bold=True)
        if errors:
            secho('-'*9, bold=True)
        for error in errors:
            error = {key: value or '-' for key, value in error.items()}
            template = '[{row-number},{column-number}] [{code}] {message}'
            message = template.format(**error)
            secho(message)


# Main program

if __name__ == '__main__':
    cli()
