import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("rngesus.db")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_campaign(conn, campaign):
    sql = '''INSERT INTO campaigns(description, status) VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, campaign)
    conn.commit()
    return cur.lastrowid

def get_campaigns(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaigns")
    return cur.fetchall()

def update_campaign(conn, campaign):
    sql = '''UPDATE campaigns SET description = ?, status = ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, campaign)
    conn.commit()

def delete_campaign(conn, id):
    sql = 'DELETE FROM campaigns WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def create_character(conn, character):
    sql = '''INSERT INTO characters(campaign_id, role, type, backstory, attributes, primary_goal, inventory) VALUES(?, ?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, character)
    conn.commit()
    return cur.lastrowid

def get_characters(conn, campaign_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters WHERE campaign_id = ?", (campaign_id,))
    return cur.fetchall()

def update_character(conn, character):
    sql = '''UPDATE characters SET role = ?, type = ?, backstory = ?, attributes = ?, primary_goal = ?, inventory = ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, character)
    conn.commit()

def delete_character(conn, id):
    sql = 'DELETE FROM characters WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def add_chat_message(conn, chat_message):
    sql = '''INSERT INTO chat(campaign_id, user_type, message) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, chat_message)
    conn.commit()
    return cur.lastrowid

def get_chat_history(conn, campaign_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat WHERE campaign_id = ?", (campaign_id,))
    return cur.fetchall()

def main():
    database = "rngesus.db"

    sql_create_campaigns_table = """CREATE TABLE IF NOT EXISTS campaigns (
                                        id INTEGER PRIMARY KEY,
                                        description TEXT NOT NULL,
                                        status TEXT
                                    );"""

    sql_create_characters_table = """CREATE TABLE IF NOT EXISTS characters (
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

    sql_create_chat_table = """CREATE TABLE IF NOT EXISTS chat (
                                    id INTEGER PRIMARY KEY,
                                    campaign_id INTEGER NOT NULL,
                                    user_type TEXT NOT NULL,
                                    message TEXT NOT NULL,
                                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                                );"""

    conn = create_connection()

    if conn is not None:
        create_table(conn, sql_create_campaigns_table)
        create_table(conn, sql_create_characters_table)
        create_table(conn, sql_create_chat_table)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    main()