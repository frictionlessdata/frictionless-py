#!/usr/bin/env python
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
def test():
    """Run the project tests."""
    cover = coverage.coverage()
    cover.start()
    test_path = os.path.abspath(os.path.join(os.path.dirname(CLI_DIR), 'tests'))
    suite = unittest.TestLoader().discover(test_path)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    cover.stop()
    cover.report()


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
