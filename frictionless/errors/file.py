from __future__ import annotations
from .data import DataError


class FileError(DataError):
    type = "file-error"
    title = "File Error"
    description = "There is a file error."
    template = "General file error: {note}"
    tags = ["#file"]


class Md5CountError(FileError):
    type = "md5-count"
    title = "Md5 Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected md5 count: {note}"


class Sha256CountError(FileError):
    type = "sha256-count"
    title = "Sha256 Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected sha256 count: {note}"


class ByteCountError(FileError):
    type = "byte-count"
    title = "Byte Count Error"
    description = "This error can happen if the data is corrupted."
    template = "The data source does not match the expected byte count: {note}"
