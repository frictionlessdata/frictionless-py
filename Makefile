.PHONY: all coverage docker-setup docs install format github lint release test test-ci write


PACKAGE := $(shell grep '^name =' pyproject.toml | cut -d '"' -f2)
VERSION := $(shell grep '^VERSION =' ${PACKAGE}/settings.py | cut -d '"' -f2)


all:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

coverage:
	hatch run coverage

docker:
	docker build --rm -t frictionless-dev .

docs:
	hatch run docs

format:
	hatch run format

lint:
	hatch run lint

release:
	git checkout main && git pull origin && git fetch -p
	@git log --pretty=format:"%C(yellow)%h%Creset %s%Cgreen%d" --reverse -20
	@echo "\nReleasing v$(VERSION) in 10 seconds. Press <CTRL+C> to abort\n" && sleep 10
	make test && git commit -a -m 'v$(VERSION)' && git tag -a v$(VERSION) -m 'v$(VERSION)'
	git push --follow-tags

test:
	hatch run test

version:
	@echo $(VERSION)

write:
	hatch run write
