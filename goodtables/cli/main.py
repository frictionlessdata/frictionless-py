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
@click.option('--dry_run', is_flag=True)
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
def pipeline(data, schema, format, dry_run, fail_fast, row_limit, report_limit):

    """Run a Good Tables pipeline."""

    options = {}
    if schema:
        options['schema'] = {'schema': schema}

    processor = _pipeline.Pipeline(data, format=format, fail_fast=fail_fast,
                                   dry_run=dry_run, row_limit=row_limit,
                                   report_limit=report_limit)

    valid, report = processor.run()
    click.echo(json.dumps(report, ensure_ascii=True))


@cli.command()
@click.argument('data')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel']))
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
def structure(data, format, fail_fast, row_limit, report_limit):

    """Run a Good Tables StructureProcessor."""

    processor = processors.StructureProcessor(format=format, fail_fast=fail_fast,
                                              row_limit=row_limit,
                                              report_limit=report_limit)

    valid, report, data = processor.run(data)
    click.echo(json.dumps(report.generate(), ensure_ascii=True))


@cli.command()
@click.argument('data')
@click.option('--schema')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel']))
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
def schema(data, schema, format, fail_fast, row_limit, report_limit):

    """Run a Good Tables SchemaProcessor."""

    processor = processors.SchemaProcessor(schema=schema, format=format,
                                           fail_fast=fail_fast, row_limit=row_limit,
                                           report_limit=report_limit)

    valid, report, data = processor.run(data)
    click.echo(json.dumps(report.generate(), ensure_ascii=True))


if __name__ == '__main__':
    cli()
