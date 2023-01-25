from loguru import logger
from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Optional


@logger.catch
class FetchDatabase:
    def __init__(self, data_path: Path):
        kogekko_db_path = data_path / "kogekko.sqlite"
        self.database_connection: sqlite3.Connection = sqlite3.connect(kogekko_db_path)

        nest_table_query: str = """CREATE TABLE IF NOT EXISTS fetch_times
        (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            page_url TEXT UNIQUE NOT NULL,
            last_timestamp INTEGER NOT NULL
        )
        """

        sql_version = sqlite3.sqlite_version.split(".")
        if int(sql_version[0]) >= 3 and int(sql_version[1]) >= 37:
            nest_table_query += " STRICT"

        nest_table_query += ";"

        with self.database_connection:
            self.database_connection.execute(nest_table_query)
            self.database_connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.database_connection.commit()
        self.database_connection.close()

    def update_last_fetch(self, url: str) -> Optional[datetime]:
        fetch_query = self.database_connection.execute(
            "SELECT last_timestamp FROM fetch_times WHERE page_url == ?", (url,)
        )
        last_fetch: Optional[tuple[int]] = fetch_query.fetchone()

        now = datetime.now(timezone.utc)
        self.database_connection.execute(
            """INSERT INTO fetch_times(page_url,last_timestamp) VALUES(?,?)
            ON CONFLICT(page_url) DO
                UPDATE SET last_timestamp=excluded.last_timestamp;""",
            (url, int(now.timestamp())),
        )
        self.database_connection.commit()

        if last_fetch is None:
            return None

        return datetime.fromtimestamp(last_fetch[0], timezone.utc)
