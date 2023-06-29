import contextlib
import io
import os
import sys
from typing import Optional


@contextlib.contextmanager
def capture_stdout(*, cwd: Optional[str] = None):
    prev_stdout = sys.stdout
    prev_cwd = os.getcwd()
    stdout = io.StringIO()
    try:
        sys.stdout = stdout
        os.chdir(cwd or prev_cwd)
        yield stdout
    finally:
        sys.stdout = prev_stdout
        os.chdir(prev_cwd)
