#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Gamestats web module.

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

import random
import string
import urlparse

from routers import BaseRouter


# Utils

CHALLENGE_CHARSET = string.ascii_letters + string.digits

def generate_challenge(size=32):
    """Generate challenge."""
    return "".join(
        random.choice(CHALLENGE_CHARSET)
        for _ in range(size)
    )


# Gamestats

def root_download(handler, gamename, resource):
    """GET /download.asp route.

    Format (query string): /download.asp?pid=%s&hash=%s&region=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)
     - region: Game region
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if not q.get("hash", []):
        handler.send_response(200)
        handler.send_headers()
        handler.end_headers()
        handler.wfile.write(generate_challenge())
        return

    print("TODO - Download data: {}".format(q))
    handler.send_response(404)
    handler.send_headers()
    handler.end_headers()


def root_upload(handler, gamename, resource):
    """POST /upload.asp route.

    Format (query string): pid=%s&hash=%s&data=%s&region=%s
     - pid: Player ID
     - hash: SHA1(key.salt + data)
     - data: Data to upload
     - region: Game region
    """
    length = int(handler.headers.get('content-length', 0))
    body = handler.rfile.read(length)
    q = urlparse.parse_qs(body)
    print("TODO - Upload data: {}".format(q))

    handler.send_response(200)
    handler.send_headers()
    handler.end_headers()


# Gamestats2

def client_get(handler, gamename, resource):
    pass


def client_put(handler, gamename, resource):
    pass


def client_get2(handler, gamename, resource):
    pass


def client_put2(handler, gamename, resource):
    pass


# Super Smash Bros. Brawl

def custom_test(handler, gamename, resource):
    pass


def custom_client_check(handler, gamename, resource):
    pass


def custom_client_download(handler, gamename, resource):
    pass


def custom_client_wincount(handler, gamename, resource):
    pass


def custom_client_upload(handler, gamename, resource):
    pass


# Handle requests

def handle(handler, gamename, resource, resources={}):
    for prefix, callback in resources.items():
        if resource.startswith(prefix):
            print("[{}] Handle {}".format(gamename, resource))
            callback(handler, gamename, resource)
            return True

    print("[{}] Can't handle {}".format(gamename, resource))
    handler.send_response(404)
    handler.send_headers()
    handler.end_headers()
    return False


def handle_root(handler, gamename, resource):
    """Handle / routes."""
    return handle(handler, gamename, resource, {
        "download.asp": root_download,
        "upload.asp": root_upload
    })


def handle_web_client(handler, gamename, resource):
    """Handle /web/client routes."""
    return handle(handler, gamename, resource, {
        "get.asp": client_get,
        "get2.asp": client_get2,
        "put.asp": client_put,
        "put2.asp": client_put2
    })


def handle_web_custom(handler, gamename, resource):
    """Handle /web/custom routes."""
    return handle(handler, gamename, resource, {
        "test.asp": custom_test
    })


def handle_web_custom_client(handler, gamename, resource):
    """Handle /web/custom/client routes."""
    return handle(handler, gamename, resource, {
        "check.asp": custom_client_check,
        "download.asp": custom_client_download,
        "upload.asp": custom_client_upload,
        "wincount.asp": custom_client_wincount
    })


GENERIC_COMMANDS = sorted({
    "/": handle_root,
    "/web/client/": handle_web_client,
    "/web/custom/": handle_web_custom,
    "/web/custom/client/": handle_web_custom_client
}.items(), reverse=True)

COMMANDS = {
    "GET": GENERIC_COMMANDS,
    "POST": GENERIC_COMMANDS
}

class GamestatsRouter(BaseRouter):
    """Gamestats router class."""
    def __init__(self, commands=COMMANDS):
        BaseRouter.__init__(self, commands)


if __name__ == "__main__":
    router = GamestatsRouter()
