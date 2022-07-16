.PHONY: all coverage docs install format github lint release test test-ci


PACKAGE := $(shell grep '^PACKAGE =' setup.py | cut -d '"' -f2)
VERSION := $(shell head -n 1 $(PACKAGE)/assets/VERSION)
LEAD := $(shell head -n 1 LEAD.md)


all:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

coverage:
	sensible-browser coverage/index.html

docs:
	python docs/build.py

format:
	black $(PACKAGE) tests

install:
	pip install --upgrade -e .[aws,bigquery,ckan,dev,excel,github,gsheets,html,ods,pandas,spss,sql,zenodo]

lint:
	black $(PACKAGE) tests --check
	pylama $(PACKAGE) tests
	pyright $(PACKAGE) tests

release:
	git checkout main && git pull origin && git fetch -p
	# TODO: recover (failing ATM)
	# @make docs && echo '\nWe are including a docs update to the commit\n'
	@git log --pretty=format:"%C(yellow)%h%Creset %s%Cgreen%d" --reverse -20
	@echo "\nReleasing v$(VERSION) in 10 seconds. Press <CTRL+C> to abort\n" && sleep 10
	make test && git commit -a -m 'v$(VERSION)' && git tag -a v$(VERSION) -m 'v$(VERSION)'
	git push --follow-tags

test:
	make lint
	pytest --cov ${PACKAGE} --cov-report term-missing --cov-report html:coverage --cov-fail-under 70 --timeout=300

test-ci:
	make lint
	pytest --cov ${PACKAGE} --cov-report term-missing --cov-report xml --cov-fail-under 80 --timeout=300 --ci
