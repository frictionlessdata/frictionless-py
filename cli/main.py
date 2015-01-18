#!/usr/bin/env python
import os
import unittest
import click
import coverage


CLI_DIR = os.path.abspath(os.path.dirname(__file__))


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


if __name__ == '__main__':
    cli()
