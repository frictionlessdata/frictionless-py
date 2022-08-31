import os
import secrets
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from .config import Config
from .. import helpers


class Session:
    token: str
    public: Path
    private: Path

    def __init__(self, config: Config, *, token: Optional[str] = None):
        # TODO: validate token
        token = token or secrets.token_urlsafe(16)
        base = Path(config.basepath)
        public = base / token
        private = base / token / ".frictionless"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)
        self.token = token
        self.public = public
        self.private = private

    # Props

    @property
    def basepath(self):
        return str(self.public)

    # Files

    def create_file(self, file: UploadFile):
        # TODO: use streaming
        # TODO: handle errors
        # TODO: sanitize filename
        path = str(self.public / file.filename)
        body = file.file.read()
        helpers.write_file(path, body, mode="wb")
        return file.filename

    def delete_file(self, path: str):
        # TODO: ensure that path is safe
        os.remove(self.public / path)
        return path

    def list_files(self):
        return [path for path in os.listdir(self.public) if not path.startswith(".")]
