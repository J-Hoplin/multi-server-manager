"""
SQL Queries

- These SQL Queries are for table: 'connections'
- Do not change the table name or column names.
- Do not add raw queries in application code
"""


GENERATE_CONNECTION_TABLE = """
CREATE TABLE IF NOT EXISTS connections (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))), -- UUID 형식
    name TEXT NOT NULL,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    user TEXT NOT NULL,
    connection_type TEXT CHECK(connection_type IN ('key', 'password')) NOT NULL,
    password TEXT,
    key_file TEXT,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

LIST_CONNECTION_TABLE = """
SELECT * FROM connections ORDER BY created_at DESC;
"""

INSERT_CONNECTION_TABLE = """
INSERT INTO connections (name, ip_address, port, connection_type, password, key_file) VALUES (?, ?, ?, ?, ?, ?);
"""

UPDATE_CONNECTION_TABLE = """
UPDATE connections SET name=?, ip_address=?, port=?, connection_type=?, password=?, key_file=? WHERE id=?;
"""

DELETE_CONNECTION_TABLE = """
DELETE FROM connections WHERE id=?;
"""
