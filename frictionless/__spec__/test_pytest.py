from pathlib import Path

import pytest

pytest_plugins = ["pytester"]


@pytest.mark.parametrize(
    "options, passed, deselected",
    [
        ([], 1, 1),
        (["-m", "sample"], 1, 1),
        (["-m", "ci"], 0, 2),
        (["-m", "ci or sample"], 1, 1),
        (["--ci"], 2, 0),
        (["--ci", "-m", "ci"], 1, 1),
    ],
)
def test_pytest_marker_selection(pytester, monkeypatch, options, passed, deselected):
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]))
    pytester.makeconftest(
        "from frictionless.conftest import pytest_addoption, pytest_configure"
    )
    pytester.makeini("[pytest]\nmarkers =\n    sample\n    ci\n")
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.sample
        def test_sample():
            pass

        @pytest.mark.ci
        def test_integration():
            pass
        """
    )

    result = pytester.runpytest_subprocess("-q", *options)

    assert result.ret == (
        pytest.ExitCode.OK if passed else pytest.ExitCode.NO_TESTS_COLLECTED
    )
    result.assert_outcomes(passed=passed, deselected=deselected)
