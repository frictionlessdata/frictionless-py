# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import unittest
import click
import coverage


#CLI_DIR = os.path.abspath(os.path.dirname(__file__))
#REPO_DIR = os.path.abspath(os.path.dirname(os.path.dirname(CLI_DIR)))
#sys.path.insert(1, REPO_DIR)
from goodtables.pipeline import Pipeline


@click.group()
def cli():
    """The entry point into the CLI."""


@cli.command()
@click.argument('data')
@click.option('--schema')
@click.option('--format', default='csv', type=click.Choice(['csv', 'excel', 'json']))
@click.option('--dry_run', is_flag=True)
@click.option('--fail_fast', is_flag=True)
@click.option('--row_limit', default=20000, type=int)
@click.option('--report_limit', default=1000, type=int)
def validate(data, schema, format, dry_run, fail_fast, row_limit, report_limit):
    """Run a pipeline."""

    options = {}
    if schema:
        options['schema'] = {'schema': schema}

    pipeline = Pipeline(data, format=format, fail_fast=fail_fast,
                        dry_run=dry_run, row_limit=row_limit,
                        report_limit=report_limit)
    valid, report = pipeline.run()

    if valid:
        click.echo('The data source is valid.\n')
    else:
        click.echo('The data source is not valid.\n')
    click.echo('Following is a report::\n')
    click.echo(report)


if __name__ == '__main__':
    cli()
