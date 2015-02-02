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


CLI_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_DIR = os.path.abspath(os.path.dirname(CLI_DIR))
sys.path.insert(1, REPO_DIR)
from tabular_validator.pipeline import ValidationPipeline


@click.group()
def cli():
    """The entry point into the CLI."""


@cli.command()
@click.argument('data_source')
def pipeline(data_source):
    """Run a validation pipeline over a data source."""

    pipeline = ValidationPipeline(data_source=data_source)
    valid, report = pipeline.run()

    if valid:
        click.echo('The data source is valid.')
    else:
        click.echo('The data source is not valid.')
    click.echo('Following is a report::\n')
    click.echo(report)


if __name__ == '__main__':
    cli()
