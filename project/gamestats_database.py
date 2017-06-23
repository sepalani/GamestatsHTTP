#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Gamestats Database module.

    GamestatsHTTP Server Project
    Copyright (C) 2017  Sepalani

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sqlite3

from contextlib import closing
from datetime import datetime

DATABASE_PATH = "gamestats2.db"
DATABASE_TIMEOUT = 5.0


def init(path=DATABASE_PATH):
    """Initialize Gamestats database."""
    conn = sqlite3.connect(path, timeout=DATABASE_TIMEOUT)
    c = conn.cursor()

    # Gamestats
    c.execute("CREATE TABLE IF NOT EXISTS storage"
              " (gamename TEXT, pid INT, region TEXT, data TEXT,"
              " updated DATETIME)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_storage"
              " ON storage (gamename, pid, region)")

    # Gamestats2
    c.execute("CREATE TABLE IF NOT EXISTS ranking"
              " (gamename TEXT, pid INT, region INT, category INT,"
              " score INT, data TEXT, updated DATETIME)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_ranking"
              " ON ranking (gamename, pid, region, category)")

    conn.commit()
    conn.close()


class GamestatsDatabase(object):
    """Gamestats database class."""
    def __init__(self, path=DATABASE_PATH):
        self.path = path
        self.conn = sqlite3.connect(self.path, timeout=DATABASE_TIMEOUT)
        self.conn.row_factory = sqlite3.Row
        self.conn.text_factory = bytes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.conn.close()

    def root_download(self, gamename, pid, region):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM storage"
                " WHERE gamename = ? AND pid = ? AND region = ?",
                (gamename, pid, region)
            )
            return cursor.fetchone()

    def root_upload(self, gamename, pid, region, data):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO storage VALUES (?,?,?,?,?)",
                (gamename, pid, region, data, datetime.now())
            )
        self.conn.commit()

    def web_put2(self, gamename, pid, region, category, score, data):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO ranking VALUES (?,?,?,?,?,?,?)",
                (gamename, pid, region, category, score, data, datetime.now())
            )
        self.conn.commit()


def root_download(gamename, pid, region, db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.root_download(gamename, pid, region)


def root_upload(gamename, pid, region, data, db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.root_upload(gamename, pid, region, data)


def web_put2(gamename, pid, region, category, score, data,
             db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.web_put2(gamename, pid, region, category, score, data)


if __name__ == "__main__":
    pass
