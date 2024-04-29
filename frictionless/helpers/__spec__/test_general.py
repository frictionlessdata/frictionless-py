import os

import pytest

from frictionless import helpers, platform

# General


def test_ensure_dir(tmpdir):
    dir_path = os.path.join(tmpdir, "dir")
    file_path = os.path.join(dir_path, "file")
    assert not os.path.isdir(dir_path)
    helpers.ensure_dir(file_path)
    assert os.path.isdir(dir_path)


@pytest.mark.parametrize(
    "path,is_safe",
    (
        ("data.csv", True),
        ("data/data.csv", True),
        ("data/country/data.csv", True),
        ("data\\data.csv", True),
        ("data\\country\\data.csv", True),
        ("../data.csv", False),
        ("~/data.csv", False),
        ("~invalid_user/data.csv", False),
        ("%userprofile%", False),
        ("%unknown_windows_var%", False),
        ("$HOME", False),
        ("$UNKNOWN_VAR", False),
    ),
)
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_is_safe_path(path, is_safe):
    assert helpers.is_safe_path(path) is is_safe
