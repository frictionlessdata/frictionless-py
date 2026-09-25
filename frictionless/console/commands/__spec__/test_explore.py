from __future__ import annotations

from types import SimpleNamespace

from frictionless.console import console
from frictionless.console.commands import explore as explore_module

from .conftest import create_runner

runner = create_runner()


def test_console_explore_passes_paths_without_shell(monkeypatch, tmp_path):
    source = tmp_path / "table;echo injected.csv"
    source.write_text("name\nvalue\n")

    calls = []

    def fake_run(args, check):
        calls.append((args, check))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(explore_module.subprocess, "run", fake_run)

    result = runner.invoke(console, ["explore", str(source)])

    assert result.exit_code == 0
    assert calls == [(["vd", "--", str(source)], False)]
    # The "--" end-of-options separator prevents a path starting with "-"
    # from being interpreted by VisiData as an option (e.g. --config, which
    # execs Python)
    args = calls[0][0]
    assert args[:2] == ["vd", "--"]
    assert all(not arg.startswith("-") for arg in args[2:])
