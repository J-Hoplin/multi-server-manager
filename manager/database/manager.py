import sqlite3
from threading import Lock
from manager.database.sql.connections import (
    GENERATE_CONNECTION_TABLE,
    LIST_CONNECTION_TABLE,
    DELETE_CONNECTION_TABLE,
)


class ApplicationPersistManager:
    """
    Application Persist Manger

    - Use SQLite3 to gurantee local
    """

    __instance = None
    __lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
            return cls.__instance

    def __init__(self):
        self.conn = sqlite3.connect("application.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(GENERATE_CONNECTION_TABLE)
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def add_connection(
        self, name, host, port, user, connection_type, password=None, key_file=None
    ):
        self.cursor.execute(
            """
            INSERT INTO connections
            (name, host, port, user, connection_type, password, key_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (name, host, port, user, connection_type, password, key_file),
        )

        self.conn.commit()

    def get_connections(self):
        self.cursor.execute(LIST_CONNECTION_TABLE)
        return self.cursor.fetchall()

    def delete_connection(self, connection_id):
        self.cursor.execute(DELETE_CONNECTION_TABLE, (connection_id,))
        self.conn.commit()

    def update_connection(
        self,
        connection_id,
        name,
        host,
        port,
        user,
        connection_type,
        password=None,
        key_file=None,
    ):
        self.cursor.execute(
            """
            UPDATE connections
            SET name = ?,
                host = ?,
                port = ?,
                user = ?,
                connection_type = ?,
                password = ?,
                key_file = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (
                name,
                host,
                port,
                user,
                connection_type,
                password,
                key_file,
                connection_id,
            ),
        )

        self.conn.commit()
