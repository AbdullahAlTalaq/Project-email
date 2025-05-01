# contact_utils.py

import sqlite3

CONTACTS_TABLE = "contacts"
DB_PATH = "tmp_yahya/agents.db"  # Same as agent_storage

def create_contacts_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CONTACTS_TABLE} (
            name TEXT PRIMARY KEY,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_contact(name: str, email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR REPLACE INTO {CONTACTS_TABLE} (name, email) VALUES (?, ?)
    """, (name.lower(), email))
    conn.commit()
    conn.close()

def get_email_by_name(name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT email FROM {CONTACTS_TABLE} WHERE name = ?
    """, (name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
