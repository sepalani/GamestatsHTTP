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
from datetime import datetime, timedelta

DATABASE_PATH = "gamestats2.db"
DATABASE_TIMEOUT = 5.0


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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

    # Smash Bros. Service
    c.execute("CREATE TABLE IF NOT EXISTS sbs_data"
              " (gamename TEXT, pid INT, sbs_type INT,"
              " sake_id INT, sake_size INT, info TEXT,"
              " delivery DATETIME)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_sake_id"
              " ON sbs_data (gamename, sbs_type, sake_id)")

    c.execute("CREATE TABLE IF NOT EXISTS sbs_data_viewer"
              " (gamename TEXT, sbs_type INT, sake_id INT,"
              "  viewer_pid INT, seen DATETIME)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_sake_viewer_id"
              " ON sbs_data_viewer (gamename, sbs_type, sake_id, viewer_pid)")

    # Ban system
    c.execute("CREATE TABLE IF NOT EXISTS bans"
              " (gamename TEXT, pid INT, region INT, comment TEXT,"
              " updated DATETIME)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_ban"
              " ON bans (gamename, pid, region)")

    conn.commit()
    conn.close()


def get2_dictrow(gamename, pid, region, category,
                 score=0, data=b"", updated=0):
    return {
        "gamename": gamename,
        "pid": pid,
        "region": region,
        "category": category,
        "score": score,
        "data": data,
        "updated": updated
    }


def sort_rows(data, rows, mine=None):
    """Sort rows."""
    # We sort rows manually if "mine" row is present.
    if mine:
        # Indeed, sorting "nearby" modes is hard to deal with using SQL only.
        # Moreover, only the "mine" row holds the order value.
        rows.sort(
            key=lambda r: r["score"],
            reverse=bool(data.get("filter", 1))  # 0=ASC, 1=DESC
        )
        return [mine] + rows
    # Rows already sorted, we need to set the order value
    for i, row in enumerate(rows):
        rows[i]["order"] = i + 1
    return rows


def filter_bans():
    return (
        " AND pid NOT IN ("
        " SELECT pid FROM bans"
        " WHERE gamename = :gamename AND (region & :region)"
        ")"
    )


def get_row_mine(cursor, parameters):
    # Retrieve user's row
    cursor.execute(
        "SELECT * FROM ranking"
        " WHERE gamename = :gamename AND region & :region"
        " AND category = :category AND pid = :pid",
        parameters
    )
    mine = cursor.fetchone()

    # Default row if it doesn't exist
    if not mine:
        mine = get2_dictrow(
            parameters["gamename"],
            parameters["pid"],
            0xFFFFFFFF,
            parameters["category"]
        )

    # Compute the row's order
    parameters["score"] = mine["score"]
    where_filter = (
        " WHERE gamename = :gamename AND region & :region"
        " AND category = :category" + filter_bans()
    )
    if parameters.get("filter", 1):
        where_filter += " AND score > :score"  # DESC
    else:
        where_filter += " AND score < :score"  # ASC
    cursor.execute(
        "SELECT COUNT(*) AS total FROM ranking" + where_filter,
        parameters
    )
    total = cursor.fetchone()["total"]
    mine["order"] = 1 + total
    return mine


class GamestatsDatabase(object):
    """Gamestats database class."""
    FILTERS = {
        0: "ASC",
        1: "DESC"
    }

    def __init__(self, path=DATABASE_PATH):
        self.path = path
        self.conn = sqlite3.connect(self.path, timeout=DATABASE_TIMEOUT)
        self.conn.row_factory = dict_factory
        self.conn.text_factory = bytes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.conn.close()

    def get_games(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                'SELECT gamename,'
                ' COUNT(*) AS "stats",'
                ' (SELECT COUNT(*) FROM bans'
                ' WHERE bans.gamename = ranking.gamename) AS "bans"'
                ' FROM ranking GROUP BY gamename'
            )
            return cursor.fetchall()

    def get_users(self, gamename):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                'SELECT gamename, pid, region, category, score, updated,'
                ' COUNT(*) AS "stats",'
                ' (SELECT COUNT(*) FROM bans'
                ' WHERE bans.gamename = :gamename'
                ' AND bans.pid = ranking.pid'
                ' AND bans.region & ranking.region) AS "bans"'
                ' FROM ranking'
                ' WHERE gamename = :gamename'
                ' GROUP BY pid, region', {
                    "gamename": gamename
                }
            )
            return cursor.fetchall()

    def has_ban(self, gamename, pid, region):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM bans"
                " WHERE gamename = ? AND pid = ? AND region & ?",
                (gamename, pid, region)
            )
            return cursor.fetchone()

    def get_bans_from(self, gamename):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM bans WHERE gamename = ?",
                (gamename,)
            )
            return cursor.fetchall()

    def get_bans(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM bans")
            return cursor.fetchall()

    def create_ban(self, gamename, pid, region, comment):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO bans VALUES (?,?,?,?,?)",
                (gamename, pid, region, comment, datetime.now())
            )
        self.conn.commit()

    def delete_ban(self, gamename, pid, region):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM bans"
                " WHERE gamename = ? AND pid = ? AND (region & ?) > 0",
                (gamename, pid, region)
            )
        self.conn.commit()

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
        # Ban system
        if self.has_ban(gamename, pid, region):
            raise ValueError("User {} banned from {}".format(pid, gamename))

        with closing(self.conn.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO ranking VALUES (?,?,?,?,?,?,?)",
                (gamename, pid, region, category, score, data, datetime.now())
            )
        self.conn.commit()

    def web_get2_own(self, gamename, pid, region, category, data):
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit")
            }
            limit = " LIMIT :limit" if data.get("limit", 0) else ""
            where_filter = (
                " WHERE gamename = :gamename AND region & :region"
                " AND category = :category" + filter_bans() +
                " AND updated >= :updated"
            )
            cursor.execute(
                "SELECT * FROM ranking" + where_filter +
                " ORDER BY score {}".format(
                    self.FILTERS.get(data.get("filter"), "")
                ) + limit, parameters
            )
            rows = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking" + where_filter,
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, rows)

    def web_get2_top(self, gamename, pid, region, category, data):
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit", 10),
                "filter": data.get("filter"),
            }
            where_filter = (
                " WHERE gamename = :gamename AND region & :region"
                " AND category = :category" + filter_bans() +
                " AND updated >= :updated"
            )
            cursor.execute(
                "SELECT * FROM ranking" + where_filter +
                " ORDER BY score {} LIMIT :limit".format(
                    self.FILTERS.get(data.get("filter"), "")
                ),
                parameters
            )
            rows = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking" + where_filter,
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, rows)

    def web_get2_nearby(self, gamename, pid, region, category, data):
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit", 10) - 1,
                "filter": data.get("filter"),
            }
            mine = get_row_mine(cursor, parameters)
            parameters["score"] = mine["score"]
            where_filter = (
                " WHERE gamename = :gamename AND region & :region"
                " AND category = :category" + filter_bans() +
                " AND pid != :pid AND updated >= :updated"
            )
            cursor.execute(
                "SELECT * FROM ranking" + where_filter +
                " ORDER BY ABS(:score - score) LIMIT :limit",
                parameters
            )
            others = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking" + where_filter,
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, others, mine)

    def web_get2_friends(self, gamename, pid, region, category, data):
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit", 10) - 1,
                "filter": data.get("filter"),
            }
            mine = get_row_mine(cursor, parameters)
            pids = ", ".join("{}".format(i) for i in data.get("friends", []))
            cursor.execute(
                "SELECT * FROM ranking"
                " WHERE gamename = :gamename AND region = :region"
                " AND category = :category"
                " AND pid IN ({}) AND updated >= :updated"
                " ORDER BY score LIMIT :limit".format(pids),
                parameters
            )
            friends = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking"
                " WHERE gamename = :gamename AND region = :region"
                " AND category = :category"
                " AND pid IN ({}) AND updated >= :updated".format(pids),
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, friends, mine)

    def web_get2_nearhi(self, gamename, pid, region, category, data):
        # TODO - Nearby high?
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit", 10) - 1,
                "filter": data.get("filter"),
            }
            mine = get_row_mine(cursor, parameters)
            parameters["score"] = mine["score"]
            where_filter = (
                " WHERE gamename = :gamename AND region & :region"
                " AND category = :category" + filter_bans() +
                " AND pid != :pid AND score >= :score"
                " AND updated >= :updated"
            )
            cursor.execute(
                "SELECT * FROM ranking" + where_filter +
                " ORDER BY score ASC LIMIT :limit",
                parameters
            )
            others = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking" + where_filter,
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, others, mine)

    def web_get2_nearlo(self, gamename, pid, region, category, data):
        # TODO - Nearby low?
        with closing(self.conn.cursor()) as cursor:
            parameters = {
                "gamename": gamename,
                "pid": pid,
                "region": region,
                "category": category,
                "updated": data["since"],
                "limit": data.get("limit", 10) - 1,
                "filter": data.get("filter"),
            }
            mine = get_row_mine(cursor, parameters)
            parameters["score"] = mine["score"]
            where_filter = (
                " WHERE gamename = :gamename AND region & :region"
                " AND category = :category" + filter_bans() +
                " AND pid != :pid AND score <= :score"
                " AND updated >= :updated"
            )
            cursor.execute(
                "SELECT * FROM ranking" + where_filter +
                " ORDER BY score DESC LIMIT :limit",
                parameters
            )
            others = cursor.fetchall()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM ranking" + where_filter,
                parameters
            )
            total = cursor.fetchone()["total"]
            return total, sort_rows(data, others, mine)

    def web_get2(self, gamename, pid, region, category, mode, data):
        # Ban system
        if self.has_ban(gamename, pid, region):
            raise ValueError("User {} banned from {}".format(pid, gamename))

        # Time filter
        if data.get("updated", 0):
            data["since"] = datetime.now() - timedelta(minutes=data["updated"])
        else:
            data["since"] = datetime(1970, 1, 1)

        # Handle mode
        if mode == 0:
            return self.web_get2_own(gamename, pid, region, category, data)
        elif mode == 1:
            return self.web_get2_top(gamename, pid, region, category, data)
        elif mode == 2:
            return self.web_get2_nearby(gamename, pid, region, category, data)
        elif mode == 3:
            return self.web_get2_friends(gamename, pid, region, category, data)
        elif mode == 4:
            # Blind guess
            return self.web_get2_nearhi(gamename, pid, region, category, data)
        elif mode == 5:
            # Blind guess
            return self.web_get2_nearlo(gamename, pid, region, category, data)
        raise ValueError("Unknown get2 mode: {}".format(mode))

    def sbs_check(self, gamename, pid, packet_type):
        # TODO - Check storage size
        return True

    def sbs_download(self, gamename, pid, packet_type):
        try:
            with closing(self.conn.cursor()) as cursor:
                sbs_type = 1 if packet_type == 0 else 2
                cursor.execute(
                    "SELECT * FROM sbs_data"
                    " WHERE gamename = ? AND sbs_type = ?"
                    " AND NOT EXISTS ("
                    "     SELECT 1 FROM sbs_data_viewer"
                    "     WHERE sbs_data.gamename = sbs_data_viewer.gamename"
                    "     AND sbs_data.sbs_type = sbs_data_viewer.sbs_type"
                    "     AND sbs_data.sake_id = sbs_data_viewer.sake_id"
                    "     AND viewer_pid = ?"
                    " ) LIMIT 1",
                    (gamename, sbs_type, pid)
                )
                sbs = cursor.fetchone()
                if sbs:
                    cursor.execute(
                        "INSERT INTO sbs_data_viewer VALUES (?,?,?,?,?)",
                        (sbs["gamename"], sbs["sbs_type"], sbs["sake_id"],
                         pid, datetime.now())
                    )
                    self.conn.commit()
                    return sbs["sake_id"], sbs["sake_size"], datetime.strptime(
                        sbs["delivery"],
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
        except Exception as e:
            pass
        return None, 0, datetime.now()

    def sbs_wincount(self, gamename, pid, sake_fileid):
        # TODO - Win count
        return True

    def sbs_upload(self, gamename, pid, packet_type,
                   sake_fileid, sake_filesize, battle_info):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO sbs_data VALUES (?,?,?,?,?,?,?)",
                    (gamename, pid, packet_type,
                     sake_fileid, sake_filesize, battle_info,
                     datetime.now())
                )
            self.conn.commit()
            return True
        except Exception as e:
            return False


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


def web_get2(gamename, pid, region, category, mode, data,
             db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.web_get2(gamename, pid, region, category, mode, data)


def sbs_check(gamename, pid, packet_type,
              db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.sbs_check(gamename, pid, packet_type)


def sbs_download(gamename, pid, packet_type,
                 db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.sbs_download(gamename, pid, packet_type)


def sbs_wincount(gamename, pid, sake_fileid,
                 db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.sbs_wincount(gamename, pid, sake_fileid)


def sbs_upload(gamename, pid, packet_type,
               sake_fileid, sake_filesize, battle_info,
               db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.sbs_upload(
            gamename, pid, packet_type,
            sake_fileid, sake_filesize, battle_info
        )


def get_games(db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.get_games()


def get_users(gamename, db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.get_users(gamename)


def has_ban(gamename, pid, region, db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.has_ban(gamename, pid, region)


def get_bans_from(gamename, db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.get_bans_from(gamename)


def get_bans(db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.get_bans()


def create_ban(gamename, pid, region, comment,
               db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.create_ban(gamename, pid, region, comment)


def delete_ban(gamename, pid, region,
               db_path=DATABASE_PATH):
    with GamestatsDatabase(db_path) as db:
        return db.delete_ban(gamename, pid, region)


if __name__ == "__main__":
    from cmd import Cmd

    def to_int(name, value):
        try:
            return int(value)
        except Exception:
            print("ERROR: `{}` needs to be an integer".format(name))
            return None

    def to_str(value):
        if isinstance(value, str):
            return value
        elif isinstance(value, bytes):
            return "".join(chr(b) for b in value)
        return str(value)

    def sanitize(d, *args):
        """Sanitize values since sqlite doesn't enforce type."""
        if not args:
            # Sanitize the whole dict
            return {k: to_str(v) for k, v in d.items()}
        return (to_str(d[arg]) for arg in args)

    def sanitize_list(ls):
        """Sanitize list elements."""
        return [sanitize(e) for e in ls]

    class GamestatsGameCmd(Cmd):
        """Commands:
        show bans [pid]
        show stats [pid]
        ban pid region_mask [comment]
        unban pid region_mask
        """

        def do_show(self, inp):
            """
            show (bans|stats) [pid]
                Show all bans/stats or the pid's ban/stats.
            """
            parameters = inp.split(None, 1)
            if len(parameters) == 1:
                mode = parameters[0]
                pid = None
            elif len(parameters) == 2:
                mode, pid = parameters
                pid = to_int("pid", pid)
                if pid is None:
                    return
            else:
                print("ERROR: Invalid parameter count!")
                return
            if mode == "bans":
                ban_list = get_bans_from(self.gamename)
                if pid is not None:
                    ban_list = [
                        u for u in ban_list
                        if u["pid"] == pid
                    ]
                line_fmt = "| {:10s} | {:6s} | {:26s} | {:23s} |"
                print(line_fmt.format("pid", "region", "date", "comment"))
                print("|-{}-|-{}-|-{}-|-{}-|".format(
                    "-"*10, "-"*6, "-"*26, "-"*23
                ))
                for user in ban_list:
                    print(line_fmt.format(
                        *sanitize(user, "pid", "region", "updated", "comment")
                    ))
            elif mode == "stats":
                user_list = get_users(self.gamename)
                # Hide stats from banned users unless the pid is specified
                if pid is None:
                    user_list = [u for u in user_list if u["bans"] == 0]
                else:
                    user_list = [u for u in user_list if u["pid"] == pid]
                line_fmt = "| {:10s} | {:6s} | {:8s} | {:10s} | {:26s} |"
                print(line_fmt.format("pid", "region", "category", "score",
                                      "date"))
                print("|-{}-|-{}-|-{}-|-{}-|-{}-|".format(
                    "-"*10, "-"*6, "-"*8, "-"*10, "-"*26
                ))
                for user in user_list:
                    print(line_fmt.format(
                        *sanitize(user, "pid", "region", "category", "score",
                                  "updated")
                    ))
            else:
                print("ERROR: Invalid mode `{}`".format(mode))

        def complete_show(self, text, line, begidx, endidx):
            user_list = [u for u in self.users]
            argidx = len(line.split())
            argidx += int(argidx > 1 and not text)
            if argidx == 1:
                return ["bans", "stats"]
            elif argidx == 2:
                return ["bans"] if "bans".startswith(text) \
                    else ["stats"] if "stats".startswith(text) \
                    else []
            elif argidx == 3:
                return [
                    u["pid"]
                    for u in user_list
                    if u["pid"].startswith(text)
                ]
            return []

        def do_ban(self, inp):
            """
            ban pid region_mask [comment]
                Ban the pid based on the region mask (65535 = all regions).
            """
            parameters = inp.split(None, 2)
            if len(parameters) < 2:
                print("ERROR: Missing parameters!")
                return
            if len(parameters) == 2:
                pid, region_mask = parameters
                comment = ""
            else:
                pid, region_mask, comment = parameters
            pid = to_int("pid", pid)
            region_mask = to_int("region_mask", region_mask)
            if pid is not None and region_mask is not None:
                create_ban(self.gamename, pid, region_mask, comment)
                print("INFO: PID {} banned from region {} (reason: {})".format(
                    pid, region_mask, comment
                ))
                self.do_refresh("")

        def complete_ban(self, text, line, begidx, endidx):
            argv = line.split()
            argc = len(argv) + int(len(argv) > 1 and not text)
            user_list = []
            if 1 <= argc <= 3:
                user_list = [
                    u for u in self.users
                    if u["bans"] == "0"
                ]
                if argc >= 2:
                    pid = text if argc == 2 else argv[1]
                    user_list = [
                        u for u in user_list
                        if u["pid"].startswith(pid)
                    ]
                if argc == 3:
                    return [
                        u["region"] for u in user_list
                        if u["region"].startswith(text)
                    ]
            return [u["pid"] for u in user_list]

        def do_unban(self, inp):
            """
            unban pid region_mask
                Unban the pid based on the region mask (65535 = all regions).
            """
            parameters = inp.split(None, 2)
            if len(parameters) < 2:
                print("ERROR: Missing parameters!")
                return
            pid, region_mask = parameters
            pid = to_int("pid", pid)
            region_mask = to_int("region_mask", region_mask)
            if pid is not None and region_mask is not None:
                delete_ban(self.gamename, pid, region_mask)
                print("INFO: PID {} unbanned from region {}".format(
                    pid, region_mask
                ))
                self.do_refresh("")

        def complete_unban(self, text, line, begidx, endidx):
            argv = line.split()
            argc = len(argv) + int(len(argv) > 1 and not text)
            user_list = []
            if 1 <= argc <= 3:
                user_list = [
                    u for u in self.users
                    if u["bans"] == "1"
                ]
                if argc >= 2:
                    pid = text if argc == 2 else argv[1]
                    user_list = [
                        u for u in user_list
                        if u["pid"].startswith(pid)
                    ]
                if argc == 3:
                    return [
                        u["region"] for u in user_list
                        if u["region"].startswith(text)
                    ]
            return [u["pid"] for u in user_list]

        def do_refresh(self, inp):
            """
            refresh
                Refresh data for the auto-completion system.
            """
            self.users = sanitize_list(get_users(self.gamename))

        def do_exit(self, inp):
            """
            Exit the game CLI.
            """
            return True

        do_EOF = do_exit

    class GamestatsCmd(Cmd):
        prompt = "\ngamestats2(http)> "
        intro = "\nGamestats2 HTTP CLI\n\nEnter '?' for help.\n"

        def do_show(self, inp):
            """
            show
                Show games ban and stats count.
            """
            self.games = sanitize_list(get_games())
            line_fmt = "| {:20s} | {:15s} | {:15s} |"
            print(line_fmt.format("gamename", "stats count", "bans count"))
            print("|-{0}-|-{1}-|-{1}-|".format("-"*20, "-"*15))
            for game in self.games:
                print(line_fmt.format(
                    game["gamename"], game["stats"], game["bans"]
                ))

        def do_use(self, gamename):
            """
            use gamename
                Use gamename's subshell.
            """
            cmd = GamestatsGameCmd()
            cmd.gamename = gamename
            cmd.prompt = "\n{}> ".format(gamename)
            cmd.users = sanitize_list(get_users(gamename))
            cmd.cmdloop()

        def complete_use(self, text, line, begidx, endidx):
            return [
                game["gamename"] for game in self.games
                if game["gamename"].startswith(text)
            ]

        def do_exit(self, inp):
            """
            Exit the CLI.
            """
            print("\nExiting...")
            return True

        do_EOF = do_exit

    try:
        cmd = GamestatsCmd()
        cmd.games = sanitize_list(get_games())
        cmd.cmdloop()
    except KeyboardInterrupt:
        pass
