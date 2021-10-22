---
title: Contributing
---

We welcome contributions from anyone! Please read the following guidelines, and feel free to reach out to us if you have questions. Thanks for your interest in helping make Frictionless awesome!

## General Guidelines

We use Github as a code and issues hosting platform. To report a bug or propose a new feature, please open an issue. For pull requests, we would ask you initially create an issue and then create a pull requests linked to this issue. If you'd like to write a tutorial, we recommend you first read this [how-to article](https://docs.google.com/document/d/1zbWMmIeU8DUwzGaEih0JGJ-DMGug5-2UksRN1x4fvj8/edit?usp=sharing) by Frictionless contributor Meyrele.

## Docs Contribution

To contribute to the documentation, please find an article in the `docs` folder and update its contents. These sections can be edited manually:
- `docs/guides`
- `docs/tutorials`

Some documentation is auto-generated (for more information see `docs/build.py`). Here is a list of auto-generated sections (excluding `overview/whats-next` docs):
- `docs/references` (from the codebase's docstrings)
- `docs/development` (from the repository root's docs)

You can test this documentation using [Livemark](https://livemark.frictionlessdata.io). Livemark in a sync mode executes Python and Bash codeblocks in Markdown and writes the results back. Here is a quick example:

> Run `livemark` against an article only if you consider the article to be a trusted source.It will execute codeblocks marked by the `script` header.

```bash
livemark sync docs/guides/basic-examples.md --diff # get the diff
livemark sync docs/guides/basic-examples.md --print # print the doc
livemark sync docs/guides/basic-examples.md # update inline
```

It's possible to run this documentation portal locally. This requires Node.js 12+ installed on your computer, and can be run with the following code:

```bash
cd site
npm install
npm start
```

Alternatively, you can run the documentation portal with Docker. With
both Docker and Docker Compose installed on the system, first build the docker container with:

```
docker build --rm -t frictionless-docs .
```

then, every time you want to run the documentation portal locally, run:

```
docker-compose up
```

then open http://localhost:3000 on a web browser to see the portal.

To update a reference in `docs/references` and some other auto-generated documents please update the codebase docstrings or root documents. For more information about auto-generated documentation see `docs/build.py`.

## Code Contribution

Frictionless is a Python3.6+ framework, and it uses some common Python tools for the development process:
- testing: `pytest`
- linting: `pylama`
- formatting: `black`
- type checking: `mypy` (under construction)

You also need `git` to work on the project, and `make` is recommended. After cloning the repository, we recommend creating a virtual environment and installing the dependencies by following this code:

> this will install a `git commit` hook running the tests

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

We also recommend running underlying commands like `pytest` or `pylama` to speed up the development process, though this is optional.

## Release Process

To release a new version:
- check that you have push access to the `master` branch
- update `frictionless/assets/VERSION` following the SemVer standard
- add changes to `CHANGELOG.md` if it's not a patch release (major or micro)
- run `make release` which create a release commit and tag and push it to Github
- an actual release will happen on the Travis CI platform after running the tests
