import warnings

warnings.filterwarnings("default", category=DeprecationWarning, module="frictionless")

from .console import console

if __name__ == "__main__":
    console(prog_name="frictionless")
