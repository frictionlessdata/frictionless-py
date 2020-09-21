# Contributing

## General Guideline

We use Github as a code and issues hosting platform. To report a bug or propose a new feature, please open an issue. For pull requests, we would ask you initially create an issue and then create a pull requests linked to this issue.

## Docs Contribution

We use a flexible documentation system as the docs are generated from:
- notebooks containing high-level guides stored in [Google Colab](https://drive.google.com/drive/folders/1boOu13YdhGkPOYiKe6KBkRmkYaaBbcsH?usp=sharing)
- source code and markdown documents within the repository

The simplest way to contribute to the guides is by leaving comments on a Google Colab document from the directory mentioned above. If you'd like to work with text files, you can contribute to the `docs/target` directory containing the built documentation. It's OK to propose changes to generated files in the `docs/target` directory as we will move the changes to the corresponding Google Colab.

To contribute to other types of documentation, please check to the corresponding `docs/name.py` file to understand the source of a document. Most of the documents outside of Google Colab are stored in the root directory of the repository; other documents are generated from the source code i.e., references.

### Building Process

In the `docs` directory we have two directories:
- data sources like Jinja2 templates: `docs/source`
- directory for generated documentation: `docs/target`

In the `docs` directory we have python scripts using:
- function to convert a Google Colab: `scripts.docs.from_notebook`
- function to copy documents: `scripts.docs.from_markdown`
- arbitrary scripts generating e.g., references

Every Python script in the `docs` directory generates one on more articles to the `docs/target` directory. You can run `make docs` to build documentation after you have set up a development environment as it's described in the next section.

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

Of course, it's possible and recommended to run underlying commands like `pytest` or `pylama` to speed up the development process.

## Release Process

To release a new version:
- check that you have push access to the `master` branch
- update `frictionless/assets/VERSION` following the SemVer standard
- add changes to `CHANGELOG.md` if it's not a patch release (major or micro)
- run `make release` which create a release commit and tag and push it to Github
- an actual release will happen on the Travis CI platform after running the tests
