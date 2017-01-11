#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Gamestats Keys module.

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

from collections import namedtuple

GamestatsKey = namedtuple("GamestatsKey", [
    "salt",
    "constants"
])
GamestatsKeyConstants = namedtuple("GamestatsKeyConstants", [
    "x",
    "y",
    "z",
    "checksum_secret"
])


def key_constants_from_str(s):
    """Return a GamestatsKeyConstants from str."""
    if len(s) >= 32:
        try:
            return GamestatsKeyConstants(
                x=int(s[0:8], 16),
                y=int(s[8:16], 16),
                z=int(s[16:24], 16),
                checksum_secret=int(s[24:32], 16)
            )
        except:
            pass
    return None


def key_from_str(s):
    """Return a GamestatsKey from str."""
    return GamestatsKey(
        salt=s[0:20] if len(s) >= 20 else None,
        constants=key_constants_from_str(s[20:52])
    )


def load_keys(path):
    """Load keys from file."""
    def helper(f):
        """Return the gamename and the key pair list."""
        for line in f:
            if not line or line[0] == '#' or not line.count(' '):
                continue
            gamename, key = line.split(' ', 1)
            yield gamename.strip(), key.strip()
        return

    with open(path, "r") as f:
        return {
            gamename.lower(): key_from_str(key)
            for gamename, key in helper(f)
        }


if __name__ == "__main__":
    pass
