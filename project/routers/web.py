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

import base64
import random
import string
import struct
try:
    # Python 2
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse
from datetime import datetime

import gamestats_database
import gamestats_keys
from routers import BaseRouter


# Utils

CHALLENGE_CHARSET = string.ascii_letters + string.digits


def generate_challenge(size=32):
    """Generate challenge."""
    return "".join(
        random.choice(CHALLENGE_CHARSET)
        for _ in range(size)
    )


def require_challenge(q, handler):
    """Send a challenge if required."""
    if not q.get("hash", []):
        handler.send_message(generate_challenge())
        return True
    return False


def decrypt_data(data, pid, key):
    """Decrypt data."""
    data_checksum = struct.unpack_from("<I", data, 0)[0]
    data = gamestats_keys.xor_data(key, data)
    checksum = gamestats_keys.do_checksum(key, data[4:])
    if checksum != data_checksum:
        raise ValueError(
            "Data checksum mismatch, 0x{:08x} expected, 0x{:08x} found".format(
                data_checksum, checksum
            )
        )
    return bytearray(data)


def decode_data(data, pid, key):
    """Decode data."""
    return decrypt_data(base64.urlsafe_b64decode(data), pid, key)


def parse_get_mode(mode_data):
    """Parse get mode."""
    parsed_data = {}
    if len(mode_data) >= 4:
        parsed_data["filter"] = struct.unpack_from("<I", mode_data, 0)[0]
    if len(mode_data) >= 8:
        parsed_data["limit"] = struct.unpack_from("<I", mode_data, 4)[0]
    if len(mode_data) >= 12:
        parsed_data["updated"] = struct.unpack_from("<I", mode_data, 8)[0]
    if len(mode_data) >= 268:
        parsed_data["friends"] = set(
            struct.unpack_from("<" + 64*"I", mode_data, 12)
        )
        if 0 in parsed_data["friends"]:
            parsed_data["friends"].remove(0)
    return parsed_data


def pack_date(date):
    """Pack date."""
    return struct.pack(
        "<IIIIII",
        date.year, date.month - 1, date.day,
        date.hour, date.minute, date.second
    )


def pack_rows(row_total, rows, mode, data, handler):
    """Pack rows."""
    now = datetime.now()
    row_count = len(rows)
    message = struct.pack("<III", mode, row_count, row_total)
    for order, row in enumerate(rows):
        # Last update
        if order == 0 and mode in [2, 3, 4, 5]:
            # Mine
            updated = 0
        else:
            try:
                row_time = datetime.strptime(
                    row["updated"],
                    "%Y-%m-%d %H:%M:%S.%f"
                )
                updated = int((now - row_time).total_seconds() // 60)
            except Exception as e:
                handler.log_message(f'Failed to parse time: {row.get("updated")}')
                updated = 0
        if updated < 0:
            handler.log_message(f"Row from the future: {row_time}")
            updated = 0
        # 4-byte alignment
        data_size = len(row["data"])
        padding = (4 - data_size % 4) % 4
        message += struct.pack(
            "<IIIIII",
            row.get("order", 0),
            row["pid"], row["score"], row["region"], updated,
            data_size + padding
        )
        message += row["data"] + padding * b"\x00"
    return message


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
    if require_challenge(q, handler):
        return

    handler.log_message(f"Download request for {gamename}: {q}")
    data = gamestats_database.root_download(
        gamename,
        q["pid"][0], q["region"][0],
        handler.server.gamestats_db
    )
    handler.log_message(
        f"Downloaded data for {gamename}: {tuple(data) if data else None}"
    )

    if not data:
        handler.send_message(code=404)
    else:
        handler.send_message(data["data"])


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

    # TODO - Check the hash

    handler.log_message(f"Upload request for {gamename}: {q}")
    data = gamestats_database.root_upload(
        gamename,
        q["pid"][0], q["region"][0], q["data"][0],
        handler.server.gamestats_db
    )

    handler.send_message()


def root_store(handler, gamename, resource):
    """GET /store.asp route.

    Format (query string): /store.asp?pid=%s&name=%s&data=%s&hash=%s&region=%s
     - pid: Player ID
     - name: Player name
     - data: Data to store
     - hash: ???
     - region: Game region
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    # TODO - Implement it properly
    handler.log_message(f"Dummy store request for {gamename}: {q}")
    handler.send_message(b"")


# Gamestats2

def client_get(handler, gamename, resource):
    """GET /web/client/get.asp route.

    Format (query string): /get.asp?pid=%d&hash=%s&data=%s
    TODO

    Example (data base64 urlsafe decoded):
     - Mode 0x02 (nearby)?
    0000  19 75 04 cf 0f 8f 93 1c  ff 00 00 00 00 00 00 00  |.u..............|
    0010  02 00 00 00 0c 00 00 00  01 00 00 00 0a 00 00 00  |................|
    0020  00 00 00 00                                       |....|
     - Mode 0x01 (top)?
    0000  19 75 05 66 0f 8f 93 1c  ff 00 00 00 00 00 00 00  |.u.f............|
    0010  01 00 00 00 0c 00 00 00  01 00 00 00 0a 00 00 00  |................|
    0020  c0 a8 00 00                                       |....|

    Description:
    19 75 04 cf - Checksum
    0f 8f 93 1c - Player ID
    ff 00 00 00 - Region mask
    00 00 00 00 - Category
    02 00 00 00 - Get mode
    0c 00 00 00 - Get mode data size
    01 00 00 00 - Row filter
    0a 00 00 00 - Row limit
    00 00 00 00 - Time filter
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"Get request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, region, category, mode, mode_data_size = \
        struct.unpack_from("<IIIIII", data)
    mode_data = data[24:24+mode_data_size]
    parsed_data = parse_get_mode(mode_data)

    # Get rows
    total, rows = gamestats_database.web_get2(
        gamename, pid, region, category, mode, parsed_data,
        handler.server.gamestats_db
    )

    # Generate response
    message = pack_rows(total, rows, mode, parsed_data, handler)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)
    return


def client_put(handler, gamename, resource):
    """GET /web/client/put.asp route.

    Format (query string): /put.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
     - mdamiiwalkds
    0000  40 1f 41 89 26 3c c7 23  04 00 00 00 03 00 00 00  |@.A.&<.#........|
    0010  50 0c 00 00 00 00 00 00                           |P.......|
     - sonicrushads
    0000  12 3f 16 97 0c 3f c7 23  04 00 00 00 00 00 00 00  |.?...?.#........|
    0010  ff 04 91 35 14 00 00 00  01 00 00 00 4d 00 61 00  |...5........M.a.|
    0020  74 00 7a 00 65 00 00 00  00 00 00 00              |t.z.e.......|
    002c

    Description:
    12 3f 16 97 - Checksum
    0c 3f c7 23 - Player ID
    04 00 00 00 - Region
    00 00 00 00 - Category
    ff 04 91 35 - Score
    14 00 00 00 - Player data size
    [...]       - Player data
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"Put request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, region, category, score, player_data_size = \
        struct.unpack_from("<IIIIII", data)

    # TODO - Check sizes (and not reuse web_put2?)
    player_data = bytes(data[24:24+player_data_size])
    gamestats_database.web_put2(
        gamename,
        pid, region, category, score, player_data,
        handler.server.gamestats_db
    )

    # Generate response
    message = b"done"
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


def client_get2(handler, gamename, resource):
    """GET /web/client/get2.asp route.

    Format (query string): /get2.asp?pid=%s&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    TODO

    Description:
    TODO
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"Get2 request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, packet_len, region, category, mode, mode_data_size = \
        struct.unpack_from("<IIIIIII", data)
    mode_data = data[28:28+mode_data_size]
    parsed_data = parse_get_mode(mode_data)

    # Get rows
    total, rows = gamestats_database.web_get2(
        gamename, pid, region, category, mode, parsed_data,
        handler.server.gamestats_db
    )

    # Generate response
    message = pack_rows(total, rows, mode, parsed_data, handler)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


def client_put2(handler, gamename, resource):
    """GET /web/client/put2.asp route.

    Format (query string): /put2.asp?pid=%s&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    0000  42 db 44 0f b7 b7 34 15  90 00 00 00 04 00 00 00  |B.D...4.........|
    0010  02 00 00 00 10 00 00 00  80 00 00 00 12 05 07 de  |................|
    0020  00 00 00 01 00 00 00 02  00 02 00 73 00 65 00 62  |...........s.e.b|
    0030  00 00 ff 55 fd c8 fb c3  00 aa ff 55 fd c8 fb e3  |...U.......U....|
    0040  a8 56 00 73 00 65 00 62  00 00 00 00 00 00 00 00  |.V.s.e.b........|
    0050  00 00 00 00 00 00 7f 51  80 76 37 77 c2 5c b9 90  |.......Q.v7w.\..|
    0060  20 0c 66 00 01 96 08 a2  08 8c 08 40 34 48 98 8d  | .f........@4H..|
    0070  30 8a 00 8a 25 05 00 00  00 00 00 00 00 00 00 00  |0...%...........|
    0080  00 00 00 00 00 00 00 00  00 00 96 f7 83 4c 41 27  |.............LA'|
    0090  74 60 82 12 15 f9 c0 c7  a4 3e 29 b6              |t`.......>).|
    009c

    Description:
    42 db 44 0f - Checksum
    b7 b7 34 15 - Player ID
    90 00 00 00 - Packet size
    04 00 00 00 - Region
    02 00 00 00 - Category
    10 00 00 00 - Score
    80 00 00 00 - Player data size
    [...]       - Player data
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"Put2 request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, packet_len, region, category, score, player_data_size = \
        struct.unpack_from("<IIIIIII", data)

    # TODO - Check sizes
    player_data = bytes(data[28:28+player_data_size])
    gamestats_database.web_put2(
        gamename,
        pid, region, category, score, player_data,
        handler.server.gamestats_db
    )

    # Generate response
    message = b"done"
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


# Super Smash Bros. Brawl


class SBS(object):
    """Smash Bros. Service"""

    class Command(object):
        """Command code."""
        UPLOAD = 0
        COMPLETE = 1
        DOWNLOAD = 2
        WINCOUNT = 3

    class Response(object):
        """Response code."""
        SUCCESS = 0
        INVALID_PID = -1
        INVALID_COMMAND = -2
        STORAGE_SIZE_FULL = -3
        RECORD_NOT_FOUND = -4
        INVALID_PID_2 = -100
        INVALID_PID_3 = -200
        NO_FILE = -201
        INVALID_PID_4 = -300
        WINCOUNT_NOT_FOUND = -301


def custom_test(handler, gamename, resource):
    pass


def custom_client_check(handler, gamename, resource):
    """GET /check.asp route.

    [SBS] CheckStorageSize function.

    Format (query string): /check.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    0000  06 91 07 8d 54 00 00 00  04 00 00 00 02 00 00 00  |....T...........|

    Description:
    06 91 07 8d - Checksum
    54 00 00 00 - Player ID
    04 00 00 00 - Packet size
    02 00 00 00 - Packet type (0x01 - Spectator, 0x02 - Submission)
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"SBS check request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, packet_len, packet_type = \
        struct.unpack_from("<IIII", data)

    # TODO - Check storage size
    if gamestats_database.sbs_check(gamename, pid, packet_type):
        response = SBS.Response.SUCCESS
    else:
        response = SBS.Response.STORAGE_SIZE_FULL

    # Generate response
    message = struct.pack("<i", SBS.Command.UPLOAD)
    message += struct.pack("<i", response)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


def custom_client_download(handler, gamename, resource):
    """GET /download.asp route.

    [SBS] GetData function.

    Request format (query string): /download.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to download

    Request example (data base64 urlsafe decoded):
    0000  06 91 05 ce fd 58 a4 1c  04 00 00 00 00 00 00 00  |.....X..........|

    Request description:
    06 91 05 ce - Checksum
    fd 58 a4 1c - Player ID
    04 00 00 00 - Packet size
    00 00 00 00 - Packet type?

    Response example:
    0000   02 00 00 00 00 00 00 00 73 c7 c8 00 d0 b5 00 00
    0010   de 07 00 00 04 00 00 00 12 00 00 00 11 00 00 00
    0020   30 00 00 00 00 00 00 00 de 07 00 00 04 00 00 00
    0030   12 00 00 00 11 00 00 00 30 00 00 00 17 00 00 00
    0040   <HMAC>

    Response description:
    02 00 00 00 - Download mode
    00 00 00 00 - Response code
    73 c7 c8 00 - Sake file id
    d0 b5 00 00 - Sake file size
    --- Delivery time
    de 07 00 00 - Year
    04 00 00 00 - Month (starts at 0)
    12 00 00 00 - Day
    11 00 00 00 - Hour
    30 00 00 00 - Minute
    00 00 00 00 - Second
    --- Current time (has to be close to delivery time)
    de 07 00 00 - Year
    04 00 00 00 - Month (starts at 0)
    12 00 00 00 - Day
    11 00 00 00 - Hour
    30 00 00 00 - Minute
    17 00 00 00 - Second
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"SBS download request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, packet_len, packet_type = \
        struct.unpack_from("<IIII", data)

    # Download
    sake_fileid, sake_filesize, delivery_date = \
        gamestats_database.sbs_download(gamename, pid, packet_type)
    if sake_fileid is not None:
        response = SBS.Response.SUCCESS
    else:
        sake_fileid = 0
        response = SBS.Response.RECORD_NOT_FOUND

    # Generate response
    current_time = delivery_date
    # current_time = datetime.now()
    message = struct.pack("<i", SBS.Command.DOWNLOAD)
    message += struct.pack("<i", response)
    message += struct.pack("<I", sake_fileid)
    message += struct.pack("<I", sake_filesize)
    message += pack_date(delivery_date)
    message += pack_date(current_time)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


def custom_client_wincount(handler, gamename, resource):
    """GET /wincount.asp route.

    [SBS] GetWinCount function.

    Format (query string): /wincount.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    0000  06 91 07 8f 54 00 00 00  04 00 00 00 01 00 00 00  |....T...........|

    Description:
    06 91 07 8f - Checksum
    54 00 00 00 - Player ID
    04 00 00 00 - Packet size
    01 00 00 00 - Sake file ID
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"SBS wincount request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)

    # Win count
    checksum, pid, packet_len, sake_fileid = \
        struct.unpack_from("<IIII", data)
    if gamestats_database.sbs_wincount(gamename, pid, sake_fileid):
        response = SBS.Response.SUCCESS
    else:
        response = SBS.Response.WINCOUNT_NOT_FOUND

    # Generate response
    message = struct.pack("<i", SBS.Command.WINCOUNT)
    message += struct.pack("<i", response)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


def custom_client_upload(handler, gamename, resource):
    """GET /upload.asp route.

    [SBS] PostData function.

    Format (query string): /upload.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    0000  06 91 05 27 54 00 00 00  14 00 00 00 01 00 00 00  |...'T...........|
    0010  75 c7 c8 00 20 0b 00 00  00 00 00 00 58 00 00 00  |u... .......X...|

    Description:
    06 91 05 27 - Checksum
    54 00 00 00 - Player ID
    14 00 00 00 - Packet size
    01 00 00 00 - Packet type (0x01 - Spectator, 0x02 - Submission)
    75 c7 c8 00 - Sake file ID
    20 0b 00 00 - Sake file size
    00 00 00 00 - Battle info 1
    58 00 00 00 - Battle info 2 (winner's pid?)
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"SBS upload request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)
    data = decode_data(q["data"][0], int(q["pid"][0]), key)
    checksum, pid, packet_len, packet_type, sake_fileid, sake_filesize, \
        battle_info1, battle_info2 = struct.unpack_from("<IIIIIIII", data)

    # Upload
    battle_info = struct.pack("<II", battle_info1, battle_info2)
    if gamestats_database.sbs_upload(gamename, pid, packet_type,
                                     sake_fileid, sake_filesize, battle_info):
        response = SBS.Response.SUCCESS
    else:
        response = SBS.Response.NO_FILE

    # Generate response
    message = struct.pack("<i", SBS.Command.COMPLETE)
    message += struct.pack("<i", SBS.Response.SUCCESS)
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


# Pokemon Battle Revolution

def pbrcheck_check(handler, gamename, resource):
    """GET /check.asp route.

    Format (query string): /check.asp?pid=%d&hash=%s&data=%s
     - pid: Player ID
     - hash: SHA1(key.salt + challenge)?
     - data: Base64 urlsafe encoded data to upload

    Example (data base64 urlsafe decoded):
    TODO

    Description:
    TODO
    """
    qs = urlparse.urlparse(resource).query
    q = urlparse.parse_qs(qs)

    # Generate challenge
    if require_challenge(q, handler):
        return

    handler.log_message(f"Dummy check request for {gamename}: {q}")
    key = handler.get_gamekey(gamename)

    # Generate response
    message = b""
    message += gamestats_keys.do_hmac(key, message)
    handler.send_message(message)


# Handle requests

def handle(handler, gamename, resource, resources={}):
    for prefix, callback in resources.items():
        if resource.startswith(prefix):
            print(f"[{gamename}] Handle {resource}")
            callback(handler, gamename, resource)
            return True

    print(f"[{gamename}] Can't handle {resource}")
    handler.send_message(code=404)
    return False


def handle_root(handler, gamename, resource):
    """Handle / routes."""
    return handle(handler, gamename, resource, {
        "download.asp": root_download,
        "upload.asp": root_upload,
        "store.asp": root_store
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


def handle_web_pbrcheck(handler, gamename, resource):
    """Handle /web/pbrcheck routes."""
    return handle(handler, gamename, resource, {
        "check.asp": pbrcheck_check
    })


GENERIC_COMMANDS = sorted({
    "/": handle_root,
    "/web/client/": handle_web_client,
    "/web/custom/": handle_web_custom,
    "/web/custom/client/": handle_web_custom_client,
    "/web/pbrcheck/": handle_web_pbrcheck
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
