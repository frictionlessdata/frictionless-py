# Contributing

We welcome contributions from anyone! Please read the following guidelines, and feel free to reach out to us if you have questions. Thanks for your interest in helping make Frictionless awesome!

## General Guidelines

We use Github as a code and issues hosting platform. To report a bug or propose a new feature, please open an issue. For pull requests, we would ask you initially create an issue and then create a pull requests linked to this issue.

## Docs Contribution

To contribute to the documentation, please find an article in the `docs` folder and update its contents. We write our documentation using [Livemark](https://livemark.frictionlessdata.io). Livemark provides an ability to provide examples without providing an output as it's generated automatically.

It's possible to run this documentation portal locally:

```bash tabs=CLI
livemark start
```

## Code Contribution

Frictionless is a Python3.8+ framework, and it uses some common Python tools for the development process (we recommend enabling support of these tools in your IDE):

- code linting: `ruff`
- import sorting: `isort`
- code formatting: `black`
- type checking: `pyright`
- code testing: `pytest`

You also need `git` to work on the project, and `make` is recommended.

After cloning the repository, you can set up the development environment
either by creating a virtual environment or a docker container.

### Using a virtual environment

Create a virtual environment and install the dependencies by following this code:

> this will install a `git commit` hook running the tests

```bash tabs=CLI
python3.8 -m venv .python
source .python/bin/activate
pip install wheel
make install  # or make install-windows
alias "frictionless=python -m frictionless"
```

Note: You may need to run `sudo apt-get install postgresql libpq-dev` on a Debian-based system, because the python Postgres module depends on some postgres CLI tools.

### Using a Docker container

Use the following command to build the container:

```bash tabs=CLI
make docker-setup
```

This should take care of setting up everything. If the container is
built without errors, you can then run commands like `make` inside the
container to accomplish various tasks (see the next section for details).

To make things easier, we can create an alias:

```bash tabs=CLI
alias "frictionless-dev=docker run --rm -v $PWD:/home/frictionless -it frictionless-dev"
```

Then, for example, to run the tests, we can use:

```bash tabs=CLI
frictionless-dev make test
```

### Using make

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
- update `frictionless/__version__` following the SemVer standard
- add changes to `CHANGELOG.md` if it's not a patch release (major or micro)
- run `make release` which create a release commit and tag and push it to Github
- an actual release will happen on the Travis CI platform after running the tests

## Running tests offline(HTTP requests) with VCR

VCR library records the response from HTTP requests locally as cassette in its first run. All subsequent calls are run using recorded metadata
from previous HTTP request, so it speeds up the testing process. To record a unit test(as cassette), we mark it with a decorator:

```python
@pytest.mark.vcr
def test_connect_with_server():
	pass
```

Cassettee will be recorded as "test_connect_with_server.yaml". A new call is made when params change. To skip sensitive data,
we can use filters:

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}
```

### Regenerating cassettes for CKAN

- Setup CKAN local instance: https://github.com/okfn/docker-ckan
- Create a sysadmin account and generate api token
- Set apikey token in .env file
```
CKAN_APIKEY=***************************
```
### Regenerating cassettes for Zenodo

**Read**
- To read, we need to use live site, the api library uses it by default.
- Login to zenodo if you have an account and create an access token.
- Set access token in .env file.
```
ZENODO_ACCESS_TOKEN=***************************
```
**Write**
- To write we can use either live site or sandbox. We recommend to use sandbox (https://sandbox.zenodo.org/api/).
- Login to zenodo(sandbox) if you have an account and create an access token.
- Set access token in .env file.
```
ZENODO_SANDBOX_ACCESS_TOKEN=***************************
```
- Set base_url in the control params
```
base_url='base_url="https://sandbox.zenodo.org/api/'
```
### Regenerating cassettes for Github

- Login to github if you have an account and create an access token(Developer settings > Personal access tokens > Tokens).
- Set access token and other details in .env file. If email/name of the user is hidden we need to provide those details as well.
```
GITHUB_NAME=FD
GITHUB_EMAIL=frictionlessdata@okfn.org
GITHUB_ACCESS_TOKEN=***************************
```
