from typing import Callable
from ...table import Row

IOnRow = Callable[[Row], None]
IOnProgress = Callable[[str], None]
