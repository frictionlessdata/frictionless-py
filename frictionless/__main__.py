import warnings

from .console import console

warnings.filterwarnings("default", category=DeprecationWarning, module="frictionless")


if __name__ == "__main__":
    console(prog_name="frictionless")
