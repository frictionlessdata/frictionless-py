from typing import Callable

from ..table import Row

IOnRow = Callable[[str, Row], None]
IOnProgress = Callable[[str, str], None]
