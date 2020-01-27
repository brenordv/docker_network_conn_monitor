# -*- coding: utf-8 -*-
from datetime import datetime
import sqlite3

from config import DATABASE_FILE


class HistoryLogger:
    def __init__(self, db_file=None):
        self.db_file = DATABASE_FILE if db_file is None else db_file

        # Database routines.
        self._db_ = None
        self._init_db_()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_db()

    def db(self):
        """
        If there's no sqlite3 database object, creates one and then returns it.
        :return: Sqlite3 database.
        """
        if self._db_ is None:
            self._db_ = sqlite3.Connection(self.db_file)

        return self._db_

    def close_db(self):
        """
        Closes the database and clears the variable.
        :return: True
        """
        if self._db_:
            self._db_.close()
            self._db_ = None

        return True

    def commit_and_close(self, cursor):
        """
        Execute a commit and then closes the cursor and database.
        :param cursor: cursor used.
        :return: True
        """
        self._db_.commit()
        cursor.close()
        self.close_db()

        return True

    def _init_db_(self):
        create_base = [
            "create table if not exists connection_history (id integer primary key autoincrement, "
            "correlation_id text not null, event text not null, event_timestamp datetime default current_timestamp, "
            "status_code int, url text, error_message text)",
        ]

        cursor = self.db().cursor()
        for query in create_base:
            cursor.execute(query)

        self.commit_and_close(cursor)
        return True

    def log_event(self, correlation_id, event, url, status_code, error_msg):
        try:
            cursor = self.db().cursor()

            cursor.execute("INSERT INTO connection_history (correlation_id, event, url, status_code, error_message) "
                           "VALUES(?, ?, ?, ?, ?)", (correlation_id, event, url, status_code, error_msg))
            self.commit_and_close(cursor)
            return True
        except Exception as e:
            print(f"Error trying to save log!\nCorrelation Id: {correlation_id}\tEvent: {event}\n"
                  f"Url: {url}\tStatus Code: {status_code}\nError: {error_msg}\n{str(e)}")

        return False

    def log_downtime(self, correlation_id, url, status_code=None, error_msg=None):
        return self.log_event(correlation_id=correlation_id, event="disconnected",
                              url=url, status_code=status_code, error_msg=error_msg)

    def log_uptime(self, correlation_id, url, status_code=None, error_msg=None):
        return self.log_event(correlation_id=correlation_id, event="connected",
                              url=url, status_code=status_code, error_msg=error_msg)

    def log_exception(self, correlation_id, url, status_code=None, error_msg=None):
        return self.log_event(correlation_id=correlation_id, event="exception",
                              url=url, status_code=status_code, error_msg=error_msg)

    def get_events(self, correlation_id=None):
        try:
            cursor = self.db().cursor()

            if correlation_id:
                cursor.execute("SELECT * FROM connection_history WHERE correlation_id = ? order by id", (correlation_id, ))
            else:
                cursor.execute("SELECT * FROM connection_history order by id")

            rows = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
            for row in rows:
                if "event_timestamp" not in row:
                    continue
                row["event_timestamp"] = datetime.strptime(row["event_timestamp"], "%Y-%m-%d %H:%M:%S")

            return rows
        except Exception as e:
            print(f"Error trying to get log!\nCorrelation Id: {correlation_id}\n{str(e)}")
