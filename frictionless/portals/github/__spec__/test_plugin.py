import pytest

from frictionless import FrictionlessException
from frictionless.portals.github.plugin import GithubControl, GithubPlugin


def test_github_plugin_parse_repo():
    test_cases = [
        {"url": "https://github.com/user/some-repo"},
        {"url": "https://github.com/user/some-repo/some-other-stuff"},
        {
            "url": "https://github.com/user/some-repo/some-stuff",
            "control": GithubControl(user="user", repo="some-repo"),
        },
    ]

    plugin = GithubPlugin()
    for test_case in test_cases:
        control = test_case["control"] if "control" in test_case else None

        adapter = plugin.create_adapter(source=test_case["url"], control=control)

        assert adapter.control.user == "user"
        assert adapter.control.repo == "some-repo"


def test_github_url_control_mismatch():
    url = "https://github.com/user/some-repo"
    control = GithubControl(user="wrong-user")

    plugin = GithubPlugin()
    with pytest.raises(FrictionlessException):
        plugin.create_adapter(source=url, control=control)
