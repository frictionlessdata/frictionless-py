# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import json
import click
from goodtables import pipeline as _pipeline
from goodtables import processors


@click.group()
def cli():
    """The entry point into the CLI."""


@cli.command()
@click.argument('data')
@click.option('--schema')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel']))
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
def pipeline(data, schema, format, fail_fast, row_limit, report_limit):

    """Run a Good Tables pipeline."""

    options = {}
    if schema:
        options['schema'] = {'schema': schema}

    processor = _pipeline.Pipeline(data, format=format, fail_fast=fail_fast,
                                   row_limit=row_limit,
                                   report_limit=report_limit)

    valid, report = processor.run()

    click.echo(json.dumps(report.generate(), ensure_ascii=True))


@cli.command()
@click.argument('data')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel']))
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
@click.option('--output', default='txt', type=click.Choice(['txt', 'json']))
def structure(data, format, fail_fast, row_limit, report_limit, output):

    """Run a Good Tables StructureProcessor."""

    processor = processors.StructureProcessor(format=format, fail_fast=fail_fast,
                                              row_limit=row_limit,
                                              report_limit=report_limit)

    valid, report, data = processor.run(data)

    valid_msg = 'Well done! The data is valid :)\n'.upper()
    invalid_msg = 'Oops.The data is invalid :(\n'.upper()

    if output == 'json':
        exclude = None
    else:
        exclude = ['result_context', 'processor', 'row_name', 'result_category',
                   'column_index', 'column_name', 'result_level']

    if valid:
        click.echo(click.style(valid_msg, fg='green'))
    else:
        click.echo(click.style(invalid_msg, fg='red'))

    click.echo(report.generate(output, exclude=exclude))

@cli.command()
@click.argument('data')
@click.option('--schema')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel']))
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
@click.option('--output', default='txt', type=click.Choice(['txt', 'json']))
def schema(data, schema, format, fail_fast, row_limit, report_limit, output):

    """Run a Good Tables SchemaProcessor."""

    processor = processors.SchemaProcessor(schema=schema, format=format,
                                           fail_fast=fail_fast, row_limit=row_limit,
                                           report_limit=report_limit)

    valid, report, data = processor.run(data)

    if output == 'json':
        exclude = None
    else:
        exclude = ['result_context', 'processor', 'row_name', 'result_category',
                   'column_index', 'column_name', 'result_level']

    valid_msg = 'Well done! The data is valid :)\n'.upper()
    invalid_msg = 'Oops.The data is invalid :(\n'.upper()

    if valid:
        click.echo(click.style(valid_msg, fg='green'))
    else:
        click.echo(click.style(invalid_msg, fg='red'))

    click.echo(report.generate(output, exclude=exclude))


if __name__ == '__main__':
    cli()
