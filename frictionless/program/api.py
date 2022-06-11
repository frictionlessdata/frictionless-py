import uvicorn
from ..server import server
from .main import program
from . import common


@program.command(name="api")
def program_api(
    port: int = common.port,
):
    """
    Start API server
    """
    uvicorn.run(server, port=port)  # type: ignore
