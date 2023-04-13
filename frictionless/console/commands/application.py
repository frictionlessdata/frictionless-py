from __future__ import annotations
import typer
import threading
import webbrowser
from ...platform import platform
from ..console import console
from .. import common


@console.command(name="application")
def console_application(
    folder: str = typer.Argument(default=None, help="Project folder [default: current]"),
    # Options
    port: int = common.port,
    debug: bool = common.debug,
):
    """
    Start Frictionless Application
    """
    module = platform.frictionless_application
    config = module.Config.from_options(
        folder=folder,
        port=port,
        debug=debug,
    )
    threading.Timer(0.1, webbrowser.open_new_tab, [f"http://localhost:{port}"]).start()
    application = module.Application.create(config)
    application.run()
