.PHONY: all install list readme release templates test version


PACKAGE := $(shell grep '^PACKAGE =' setup.py | cut -d "'" -f2)
VERSION := $(shell head -n 1 $(PACKAGE)/VERSION)
MAINTAINER := $(shell head -n 1 MAINTAINER.md)


all: list

install:
	pip install --upgrade -e .[develop,ods]

list:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

readme:
	pip install md-toc
	md_toc -p README.md github --header-levels 4
	sed -i '/(#$(PACKAGE)-py)/,+2d' README.md

release:
	git checkout master
	git pull origin
	git fetch -p
	git commit -a -m 'v$(VERSION)'
	git tag -a v$(VERSION) -m 'v$(VERSION)'
	git push --follow-tags

templates:
	sed -i -E "s/@(\w*)/@$(MAINTAINER)/" .github/issue_template.md
	sed -i -E "s/@(\w*)/@$(MAINTAINER)/" .github/pull_request_template.md

spec:
	wget -O goodtables/spec.json https://raw.githubusercontent.com/frictionlessdata/data-quality-spec/master/spec.json

test:
	pylama $(PACKAGE)
	tox

version:
	@echo $(VERSION)
