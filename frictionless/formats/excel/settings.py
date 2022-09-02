from __future__ import annotations

# General

DEFAULT_SHEET = 1
EXCEL_CODES = {
    "yyyy": "%Y",
    "yy": "%y",
    "dddd": "%A",
    "ddd": "%a",
    "dd": "%d",
    "d": "%-d",
    # Different from excel as there is no J-D in strftime
    "mmmmmm": "%b",
    "mmmm": "%B",
    "mmm": "%b",
    "hh": "%H",
    "h": "%-H",
    "ss": "%S",
    "s": "%-S",
    # Possibly different from excel as there is no am/pm in strftime
    "am/pm": "%p",
    # Different from excel as there is no A/P or a/p in strftime
    "a/p": "%p",
}

EXCEL_MINUTE_CODES = {
    "mm": "%M",
    "m": "%-M",
}
EXCEL_MONTH_CODES = {
    "mm": "%m",
    "m": "%-m",
}

EXCEL_MISC_CHARS = [
    "$",
    "+",
    "(",
    ":",
    "^",
    "'",
    "{",
    "<",
    "=",
    "-",
    "/",
    ")",
    "!",
    "&",
    "~",
    "}",
    ">",
    " ",
]

EXCEL_ESCAPE_CHAR = "\\"
EXCEL_SECTION_DIVIDER = ";"
