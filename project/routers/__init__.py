#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Gamestats routers module.

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


class BaseRouter(object):
    """Base router class."""
    def __init__(self, commands={}):
        self.commands = commands
        for command, routes in self.commands.items():
            setattr(
                self, "do_{}".format(command),
                lambda handler, gamename, path:
                self.do(handler, gamename, path, routes)
            )

    def do(self, handler, gamename, path, routes={}):
        """Perform routing."""
        for route, callback in routes:
            _, sep, resource = path.partition(route)
            if not _ and sep:
                return callback(handler, gamename, resource)
        return False


if __name__ == "__main__":
    pass
