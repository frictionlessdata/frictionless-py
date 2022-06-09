from .data import DataError


class FileError(DataError):
    code = "file-error"
    name = "File Error"
    tags = ["#data", "#file"]
    template = "General file error: {note}"
    description = "There is a file error."


class HashCountError(FileError):
    code = "hash-count"
    name = "Hash Count Error"
    template = "The data source does not match the expected hash count: {note}"
    description = "This error can happen if the data is corrupted."


class ByteCountError(FileError):
    code = "byte-count"
    name = "Byte Count Error"
    template = "The data source does not match the expected byte count: {note}"
    description = "This error can happen if the data is corrupted."
