"""
String convert functions

The MIT License (MIT)

Copyright (c) 2015 Taka Okunishi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# The "stringcase" package appears to unmaintained
# https://github.com/okunishinishi/python-stringcase/issues/42
# Relevant parts have been vendored here so we can fix warnings
# that will eventually become errors
# Code here was copied from the 1.2.0 version uploaded to PyPI
# https://pypi.org/project/stringcase/1.2.0/

import re


def camelcase(string: str):
    """Convert string into camel case.

    Args:
        string: String to convert.

    Returns:
        string: Camel case string.

    """

    string = re.sub(r"\w[\s\W]+\w", "", str(string))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(
        r"[\-_\.\s]([a-z])", lambda matched: uppercase(matched.group(1)), string[1:]
    )


def lowercase(string: str):
    """Convert string into lower case.

    Args:
        string: String to convert.

    Returns:
        string: Lowercase case string.

    """

    return str(string).lower()


def snakecase(string: str):
    """Convert string into snake case.
    Join punctuation with underscore

    Args:
        string: String to convert.

    Returns:
        string: Snake cased string.

    """

    string = re.sub(r"[\-\.\s]", "_", str(string))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(
        r"[A-Z]", lambda matched: "_" + lowercase(matched.group(0)), string[1:]
    )


def uppercase(string: str):
    """Convert string into upper case.

    Args:
        string: String to convert.

    Returns:
        string: Uppercase case string.

    """

    return str(string).upper()
