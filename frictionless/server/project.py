import os
import secrets
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from .config import Config
from .. import helpers


class Project:
    session: Optional[str]
    public: Path
    private: Path

    def __init__(self, config: Config, *, session: Optional[str] = None):
        base = Path(config.basepath or "")

        # Validate session
        # TODO: raise not authorized access
        if session:
            assert not config.root
            assert os.path.isdir(base / session)

        # Create session
        elif not config.root:
            session = secrets.token_urlsafe(16)

        # Ensure project
        public = base / (session or "")
        private = public / ".frictionless"
        public.mkdir(parents=True, exist_ok=True)
        private.mkdir(parents=True, exist_ok=True)

        # Store attributes
        self.session = session
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

    def read_file(self, path: str):
        # TODO: ensure that path is safe
        with open(self.public / path) as file:
            text = file.read()
        return text
