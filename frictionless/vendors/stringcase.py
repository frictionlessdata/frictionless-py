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
# It has been vendored here so we can fix warnings that will eventually become errors
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


def capitalcase(string: str):
    """Convert string into capital case.
    First letters will be uppercase.

    Args:
        string: String to convert.

    Returns:
        string: Capital case string.

    """

    string = str(string)
    if not string:
        return string
    return uppercase(string[0]) + string[1:]


def constcase(string: str):
    """Convert string into upper snake case.
    Join punctuation with underscore and convert letters into uppercase.

    Args:
        string: String to convert.

    Returns:
        string: Const cased string.

    """

    return uppercase(snakecase(string))


def lowercase(string: str):
    """Convert string into lower case.

    Args:
        string: String to convert.

    Returns:
        string: Lowercase case string.

    """

    return str(string).lower()


def pascalcase(string: str):
    """Convert string into pascal case.

    Args:
        string: String to convert.

    Returns:
        string: Pascal case string.

    """

    return capitalcase(camelcase(string))


def pathcase(string: str):
    """Convert string into path case.
    Join punctuation with slash.

    Args:
        string: String to convert.

    Returns:
        string: Path cased string.

    """
    string = snakecase(string)
    if not string:
        return string
    return re.sub(r"_", "/", string)


def backslashcase(string: str):
    """Convert string into spinal case.
    Join punctuation with backslash.

    Args:
        string: String to convert.

    Returns:
        string: Spinal cased string.

    """
    str1 = re.sub(r"_", r"\\", snakecase(string))

    return str1
    # return re.sub(r"\\n", "", str1))  # TODO: make regex fot \t ...


def sentencecase(string: str):
    """Convert string into sentence case.
    First letter capped and each punctuations are joined with space.

    Args:
        string: String to convert.

    Returns:
        string: Sentence cased string.

    """
    joiner = " "
    string = re.sub(r"[\-_\.\s]", joiner, str(string))
    if not string:
        return string
    return capitalcase(
        trimcase(
            re.sub(r"[A-Z]", lambda matched: joiner + lowercase(matched.group(0)), string)
        )
    )


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


def spinalcase(string: str):
    """Convert string into spinal case.
    Join punctuation with hyphen.

    Args:
        string: String to convert.

    Returns:
        string: Spinal cased string.

    """

    return re.sub(r"_", "-", snakecase(string))


def dotcase(string: str):
    """Convert string into dot case.
    Join punctuation with dot.

    Args:
        string: String to convert.

    Returns:
        string: Dot cased string.

    """

    return re.sub(r"_", ".", snakecase(string))


def titlecase(string: str):
    """Convert string into sentence case.
    First letter capped while each punctuations is capitalsed
    and joined with space.

    Args:
        string: String to convert.

    Returns:
        string: Title cased string.

    """

    return " ".join([capitalcase(word) for word in snakecase(string).split("_")])


def trimcase(string: str):
    """Convert string into trimmed string.

    Args:
        string: String to convert.

    Returns:
        string: Trimmed case string
    """

    return str(string).strip()


def uppercase(string: str):
    """Convert string into upper case.

    Args:
        string: String to convert.

    Returns:
        string: Uppercase case string.

    """

    return str(string).upper()


def alphanumcase(string: str):
    """Cuts all non-alphanumeric symbols,
    i.e. cuts all expect except 0-9, a-z and A-Z.

    Args:
        string: String to convert.

    Returns:
        string: String with cutted non-alphanumeric symbols.

    """
    # return filter(str.isalnum, str(string))
    return re.sub(r"\W+", "", string)
