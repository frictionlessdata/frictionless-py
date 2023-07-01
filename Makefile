.PHONY: all coverage docker-setup docs install format github lint release test test-ci


PACKAGE := $(shell grep '^name =' pyproject.toml | cut -d '"' -f2)
VERSION := $(shell grep '^VERSION =' ${PACKAGE}/settings.py | cut -d '"' -f2)
LEAD := $(shell head -n 1 LEAD.md)


all:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

coverage:
	sensible-browser coverage/index.html

docker-setup:
	docker build --rm -t frictionless-dev .

docs:
	livemark build

format:
	ruff $(PACKAGE) tests --fix
	isort $(PACKAGE) tests
	black $(PACKAGE) tests

install:
	pip install --upgrade -e .[aws,bigquery,ckan,csv,dev,duckdb,excel,json,github,gsheets,html,markdown,mysql,ods,pandas,parquet,postgresql,spss,sql,visidata,wkt,zenodo]

# TODO: remove when duckdb is fixed on Windows
install-windows:
	pip install --upgrade -e .[aws,bigquery,ckan,csv,dev,excel,json,github,gsheets,html,markdown,mysql,ods,pandas,parquet,postgresql,server,spss,sql,visidata,wkt,zenodo]

lint:
	ruff $(PACKAGE) tests
	isort $(PACKAGE) tests --check
	black $(PACKAGE) tests --check
	pyright $(PACKAGE) tests

release:
	git checkout main && git pull origin && git fetch -p
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
