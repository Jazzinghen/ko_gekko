# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
""" KoGekko's CLI database interface

This module implements a simple interface to a SQLite database for latest retrieval data
tracking.
"""

from datetime import datetime, timezone
from loguru import logger
from pathlib import Path
from typing import Optional
import sqlite3


@logger.catch
class FetchDatabase:
    """Class handling database interface and data retrieval

    This class is designed to be used in `with` statements as that assures the correct
    closing of the connection

    Example
    --------

    >>> with FetchDatabase(datapath) as connection:
    ...     last_fetch: Optional[datetime] = connection.update_last_fetch(url)
    ...     if last_fetch is not None:
    ...         print(f"Last time retrieved: {last_fetch}")
    Last time retrieved: 1970-01-01 01:00:00

    Attributes
    ----------
    self.database_connection : sqlite3.Connection
        Connection to the chosen database
    """

    def __init__(self, data_path: Path):
        """Initialize the dabase connection

        The database will be created and a table to store the last retrieval time will
        be created.

        Parameters
        ----------
        data_path : pathlib.Path
            Path to folder where to store the time database
        """
        kogekko_db_path = data_path / "kogekko.sqlite"
        logger.debug(f'Opening connection to database file "{kogekko_db_path}"')
        self.database_connection: sqlite3.Connection = sqlite3.connect(kogekko_db_path)

        nest_table_query: str = """CREATE TABLE IF NOT EXISTS fetch_times
        (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            page_url TEXT UNIQUE NOT NULL,
            last_timestamp INTEGER NOT NULL
        )
        """

        logger.debug(f"SQLite module is version {sqlite3.sqlite_version}")
        sql_version = sqlite3.sqlite_version.split(".")
        if int(sql_version[0]) >= 3 and int(sql_version[1]) >= 37:
            logger.debug(
                "Using strict schema definition as SQLite version is >= 3.37.0"
            )
            nest_table_query += " STRICT"

        nest_table_query += ";"
        logger.debug(f"Actual table creation query:\n\t{nest_table_query}")

        with self.database_connection:
            self.database_connection.execute(nest_table_query)

        logger.success("Completed database connection and table creation")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Closing database connection")
        self.database_connection.close()

    def update_last_fetch(self, url: str) -> Optional[datetime]:
        """Updates the last time the page was fetched

        Parameters
        ----------
        url : str
            URL retrieved

        Returns
        -------
        datetime.datetime, optional
            The last time this page was retrieved. It will be None if this is the first
            time the URL was requested
        """
        fetch_query = self.database_connection.execute(
            "SELECT last_timestamp FROM fetch_times WHERE page_url == ?", (url,)
        )
        last_fetch: Optional[tuple[int]] = fetch_query.fetchone()

        logger.debug(
            "Retrieved the following last fetch timestamp data from database: ",
            f"{last_fetch}",
        )

        last_timestamp: Optional[datetime] = None
        if last_fetch is not None:
            datetime.fromtimestamp(last_fetch[0], timezone.utc)

        now = datetime.now(timezone.utc)
        with self.database_connection:
            self.database_connection.execute(
                """INSERT INTO fetch_times(page_url,last_timestamp) VALUES(?,?)
                ON CONFLICT(page_url) DO
                    UPDATE SET last_timestamp=excluded.last_timestamp;""",
                (url, int(now.timestamp())),
            )

        return last_timestamp
