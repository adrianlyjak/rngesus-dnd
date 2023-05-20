import sqlite3
from sqlite3 import Error

def create_connection() -> sqlite3.Connection:
    conn: sqlite3.Connection = None
    try:
        conn = sqlite3.connect("rngesus.db")
    except Error as e:
        print(e)
    return conn

def create_table(create_table_sql: str, conn: sqlite3.Connection) -> None:
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_campaign(campaign: tuple, conn: sqlite3.Connection) -> int:
    sql = '''INSERT INTO campaigns(description, status) VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, campaign)
    conn.commit()
    return cur.lastrowid

def get_campaigns(conn: sqlite3.Connection) -> list:
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaigns")
    return cur.fetchall()

def update_campaign(campaign: tuple, conn: sqlite3.Connection) -> None:
    sql = '''UPDATE campaigns SET description = ?, status = ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, campaign)
    conn.commit()

def delete_campaign(id: int, conn: sqlite3.Connection) -> None:
    sql = 'DELETE FROM campaigns WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def create_character(character: tuple, conn: sqlite3.Connection) -> int:
    sql = '''INSERT INTO characters(campaign_id, role, type, backstory, attributes, primary_goal, inventory) VALUES(?, ?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, character)
    conn.commit()
    return cur.lastrowid

def get_characters(campaign_id: int, conn: sqlite3.Connection) -> list:
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters WHERE campaign_id = ?", (campaign_id,))
    return cur.fetchall()

def update_character(character: tuple, conn: sqlite3.Connection) -> None:
    sql = '''UPDATE characters SET role = ?, type = ?, backstory = ?, attributes = ?, primary_goal = ?, inventory = ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, character)
    conn.commit()

def delete_character(id: int, *, conn: sqlite3.Connection=None) -> None:
    sql = 'DELETE FROM characters WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def add_chat_message(chat_message: tuple, conn: sqlite3.Connection) -> int:
    sql = '''INSERT INTO chat(campaign_id, user_type, message) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, chat_message)
    conn.commit()
    return cur.lastrowid

def get_chat_history(campaign_id: int, conn: sqlite3.Connection) -> list:
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat WHERE campaign_id = ?", (campaign_id,))
    return cur.fetchall()

def main() -> None:

    sql_create_campaigns_table: str = """CREATE TABLE IF NOT EXISTS campaigns (
                                        id INTEGER PRIMARY KEY,
                                        description TEXT NOT NULL,
                                        status TEXT
                                    );"""

    sql_create_characters_table: str = """CREATE TABLE IF NOT EXISTS characters (
                                        id INTEGER PRIMARY KEY,
                                        campaign_id INTEGER NOT NULL,
                                        role TEXT NOT NULL,
                                        type TEXT NOT NULL,
                                        backstory TEXT,
                                        attributes TEXT,
                                        primary_goal TEXT,
                                        inventory TEXT,
                                        FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                                    );"""

    sql_create_chat_table: str = """CREATE TABLE IF NOT EXISTS chat (
                                    id INTEGER PRIMARY
                                KEY,
                                    campaign_id INTEGER NOT NULL,
                                    user_type TEXT NOT NULL,
                                    message TEXT NOT NULL,
                                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                                );"""

    conn: sqlite3.Connection = create_connection()

    if conn is not None:
        create_table(sql_create_campaigns_table, conn=conn)
        create_table(sql_create_characters_table, conn=conn)
        create_table(sql_create_chat_table, conn=conn)
    else:
        print("Error! Cannot create the database connection.")
