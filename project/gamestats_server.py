#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Gamestats HTTP server.

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

from optparse import OptionParser

try:
    # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ForkingMixIn, ThreadingMixIn
except ImportError:
    # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ForkingMixIn, ThreadingMixIn

import gamestats_keys as gs_keys
from routers.web import GamestatsRouter


class GamestatsHTTPRequestHandler(BaseHTTPRequestHandler):
    """Gamestats HTTP request handler."""
    def send_headers(self):
        """Send headers."""
        self.send_header("Content-type", "text/html")
        self.send_header("Server", "Microsoft-IIS/6.0")
        self.send_header("server", "GSTPRDSTATSWEB2")
        self.send_header("X-Powered-By", "ASP.NET")

    def parse_path(self):
        """Split the gamename and the path."""
        if self.path.count("/") >= 2:
            _, gamename, path = self.path.split("/", 2)
            if not _:
                return gamename, "/{}".format(path)
        return None, self.path

    def do_GET(self):
        gamename, path = self.parse_path()
        print("[{}] GET {}".format(gamename, path))
        print("Key: {}".format(self.server.gamestats_keys.get(gamename, None)))
        self.server.gamestats_router.do_GET(self, gamename, path)

    def do_POST(self):
        gamename, path = self.parse_path()
        print("[{}] POST {}".format(gamename, path))
        print("Key: {}".format(self.server.gamestats_keys.get(gamename, None)))
        self.server.gamestats_router.do_POST(self, gamename, path)


class GamestatsHTTPServer(HTTPServer):
    """Gamestats HTTP server."""
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.gamestats_keys = gs_keys.load_keys("gamestats_keys.txt")
        self.gamestats_router = GamestatsRouter()


class GamestatsForkingHTTPServer(ForkingMixIn, GamestatsHTTPServer):
    """Gamestats forking HTTP server."""
    pass


class GamestatsThreadingHTTPServer(ThreadingMixIn, GamestatsHTTPServer):
    """Gamestats threading HTTP server."""
    pass


def ssl_wrapper(opt, server):
    """SSL wrapper."""
    if opt.key or opt.cert:
        from ssl import wrap_socket, PROTOCOL_SSLv23

        params = {
            "ssl_version": PROTOCOL_SSLv23,
            "server_side": True
        }
        if opt.key:
            params["keyfile"] = opt.key
        if opt.cert:
            params["certfile"] = opt.cert

        server.socket = wrap_socket(server.socket, **params)

    return server


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-H", "--hostname", action="store", type=str,
                      default="0.0.0.0", dest="host",
                      help="set server hostname")
    parser.add_option("-P", "--port", action="store", type=int,
                      default=80, dest="port",
                      help="set server port")
    parser.add_option("-c", "--cert", action="store", type=str,
                      default="", dest="cert",
                      help="set HTTPS server certificate")
    parser.add_option("-k", "--key", action="store", type=str,
                      default="", dest="key",
                      help="set HTTPS server private key")
    parser.add_option("-t", "--type", action="store", type="choice",
                      choices=("base", "fork", "thread"),
                      default="base", dest="type",
                      help="set server type")
    opt, arg = parser.parse_args()

    server_classes = {
        "base": GamestatsHTTPServer,
        "fork": GamestatsForkingHTTPServer,
        "thread": GamestatsThreadingHTTPServer
    }

    server = server_classes[opt.type](
        (opt.host, opt.port),
        GamestatsHTTPRequestHandler
    )

    # HTTPS server
    server = ssl_wrapper(opt, server)

    try:
        print("Server: {} | Port: {}".format(opt.host, opt.port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Server] Closing...")
        server.server_close()
