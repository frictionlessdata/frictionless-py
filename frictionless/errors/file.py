from __future__ import annotations

from .data import DataError


class FileError(DataError):
    type = "file-error"
    title = "File Error"
    description = "There is a file error."
    template = "General file error: {note}"
    tags = ["#file"]


class HashCountError(FileError):
    type = "hash-count"
    title = "Hash Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected hash count: {note}"


class ByteCountError(FileError):
    type = "byte-count"
    title = "Byte Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected byte count: {note}"
