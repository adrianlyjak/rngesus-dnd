import sqlite3
from sqlite3 import Error
from typing import List, Dict
from pydantic import BaseModel
import json


class CreateCampaign(BaseModel):
    description: str
    character_classes: List[str]
    character_races: List[str]


class Campaign(CreateCampaign):
    id: int


class CreateCharacter(BaseModel):
    campaign_id: int
    role: str
    type: str
    backstory: str
    attributes: Dict[str, int]
    primary_goal: str
    inventory: List[str]


class Character(CreateCharacter):
    id: int


class ChatMessage(BaseModel):
    campaign_id: int
    user_type: str
    message: str


def create_connection() -> sqlite3.Connection:
    conn: sqlite3.Connection = None
    try:
        conn = sqlite3.connect("rngesus.db")
    except Error as e:
        print(e)
    return conn


def create_table(create_table_sql: str, conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(create_table_sql)


def create_campaign(campaign: CreateCampaign, conn: sqlite3.Connection) -> int:
    sql = """INSERT INTO campaigns(description, character_classes, character_races) VALUES(?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(
        sql, (campaign.description, campaign.character_classes, campaign.character_races)
    )
    conn.commit()
    return cur.lastrowid


def get_campaign(id: int, conn: sqlite3.Connection) -> Campaign:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, character_classes, character_races FROM campaigns WHERE id = ?",
        (id,),
    )
    row = cur.fetchone()
    return _parse_campaign(row)


def _parse_campaign(row: sqlite3.Row) -> Campaign:
    return Campaign.parse_obj(
        {
            "id": row[0],
            "description": row[1],
            "character_classes": json.loads(row[2]),
            "character_races": json.loads(row[3]),
        }
    )


def get_campaigns(conn: sqlite3.Connection) -> List[Campaign]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, character_classes, character_races FROM campaigns"
    )
    rows = cur.fetchall()
    return [_parse_campaign(row) for row in rows]


def delete_campaign(id: int, conn: sqlite3.Connection) -> None:
    sql = "DELETE FROM campaigns WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def create_character(character: CreateCharacter, conn: sqlite3.Connection) -> int:
    sql = """INSERT INTO characters(campaign_id, role, type, backstory, attributes, primary_goal, inventory) VALUES(?, ?, ?, ?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(
        sql,
        (
            character.campaign_id,
            character.role,
            character.type,
            character.backstory,
            character.attributes,
            character.primary_goal,
            character.inventory,
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_characters(campaign_id: int, conn: sqlite3.Connection) -> List[Character]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters WHERE campaign_id = ?", (campaign_id,))
    rows = cur.fetchall()
    return [
        Character(
            id=row[0],
            campaign_id=row[1],
            role=row[2],
            type=row[3],
            backstory=row[4],
            attributes=row[5],
            primary_goal=row[6],
            inventory=row[7],
        )
        for row in rows
    ]


def update_character(character: Character, conn: sqlite3.Connection) -> None:
    sql = """UPDATE characters SET role = ?, type = ?, backstory = ?, attributes = ?, primary_goal = ?, inventory = ? WHERE id = ?"""
    cur = conn.cursor()
    cur.execute(
        sql,
        (
            character.role,
            character.type,
            character.backstory,
            character.attributes,
            character.primary_goal,
            character.inventory,
            character.id,
        ),
    )
    conn.commit()


def delete_character(id: int, conn: sqlite3.Connection = None) -> None:
    sql = "DELETE FROM characters WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def add_chat_message(chat_message: ChatMessage, conn: sqlite3.Connection) -> int:
    sql = """INSERT INTO chat(campaign_id, user_type, message) VALUES(?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(
        sql, (chat_message.campaign_id, chat_message.user_type, chat_message.message)
    )
    conn.commit()
    return cur.lastrowid


def get_chat_history(campaign_id: int, conn: sqlite3.Connection) -> List[ChatMessage]:
    cur = conn.cursor()
    cur.execute(
        "SELECT campaign_id, user_type, message FROM chat WHERE campaign_id = ?",
        (campaign_id,),
    )
    rows = cur.fetchall()
    return [
        ChatMessage(campaign_id=row[0], user_type=row[1], message=row[2])
        for row in rows
    ]


def main() -> None:
    sql_create_campaigns_table: str = """CREATE TABLE IF NOT EXISTS campaigns (
                                        id INTEGER PRIMARY KEY,
                                        description TEXT NOT NULL,
                                        character_classes TEXT NOT NULL,
                                        character_races TEXT NOT NULL
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
                                    id INTEGER PRIMARY KEY,
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
