from __future__ import annotations
from .data import DataError


class FileError(DataError):
    name = "File Error"
    type = "file-error"
    tags = ["#file"]
    template = "General file error: {note}"
    description = "There is a file error."


class HashCountError(FileError):
    name = "Hash Count Error"
    type = "hash-count"
    template = "The data source does not match the expected hash count: {note}"
    description = "This error can happen if the data is corrupted."


class ByteCountError(FileError):
    name = "Byte Count Error"
    type = "byte-count"
    template = "The data source does not match the expected byte count: {note}"
    description = "This error can happen if the data is corrupted."
