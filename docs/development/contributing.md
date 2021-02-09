---
title: Contributing
---

## General Guideline

We use Github as a code and issues hosting platform. To report a bug or propose a new feature, please open an issue. For pull requests, we would ask you initially create an issue and then create a pull requests linked to this issue.

## Docs Contribution

We use a flexible documentation system as the docs are generated from:
- markdown documents in the `docs` directory interpreted by the Jupyter Notebook runner
- python scripts in the `docs` directory generating references or copying documents from the root directory such as `README.md`, `CHANGELOG.md` etc

To contribute to the documentation, please check to the corresponding `docs/name.md|py` file to understand the source of a document. If it's a markdown just edit it in-line if it's a script edit it or find a corresponding document in the root directory.

### Building Process

There are two main `docs` directories:
- source directory: `docs`
- target directory: `docs/build`

To build only one document run:

```bash
python scripts/docs.py name
```

To build the whole documentation:

```bash
python scripts/docs.py # or make docs
```

## Code Contribution

Frictionless is a Python3.6+ framework, and it uses some basically standard Python tools for the development process:
- testing: `pytest`
- linting: `pylama`
- formatting: `black`
- type checking: `mypy` (under construction)

It's a commonplace but, of course, you need `git` to work on the project, also `make` is recommended.

### Development Environment

After cloning the repository, it's recommended to create a virtual environment and install the dependencies:

> it will install a `git commit` hook running the tests

```bash
python3.8 -m venv .python
source .python/bin/activate
pip install wheel
make install
alias "frictionless=python -m frictionless"
```

Then you can run various make commands:
- `make docs` - build the docs
- `make format` - format source code
- `make install` - install the dependencies (we did before)
- `make lint` - lint the project
- `make release` - release a new version
- `make test` - run the tests
- `make test-ci` - run the tests (including integration)

Of course, it's possible and recommended to run underlying commands like `pytest` or `pylama` to speed up the development process.

## Release Process

To release a new version:
- check that you have push access to the `master` branch
- update `frictionless/assets/VERSION` following the SemVer standard
- add changes to `CHANGELOG.md` if it's not a patch release (major or micro)
- run `make release` which create a release commit and tag and push it to Github
- an actual release will happen on the Travis CI platform after running the tests
