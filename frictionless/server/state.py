import sqlite3
import secrets
from pathlib import Path
from .config import Config
from .. import helpers


class State:
    config: Config
    basepath: Path
    database: sqlite3.Connection

    def __init__(self, config: Config):
        self.config = config
        self.basepath = self.__prepare_basepath()
        self.database = self.__prepare_database()

    def __prepare_basepath(self):
        basepath = Path(self.config.basepath)
        helpers.ensure_folder(basepath / "sessions")
        return basepath

    def __prepare_database(self):
        path = self.basepath / "server.db"
        database = sqlite3.connect(path)
        database.execute("create table if not exists sessions(token, created)")
        return database

    # Sessions

    def create_session(self):
        token = secrets.token_urlsafe(16)
        helpers.ensure_folder(self.basepath / token / "private")
        helpers.ensure_folder(self.basepath / token / "public")
        return token
