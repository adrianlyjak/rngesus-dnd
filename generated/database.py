import sqlite3
from sqlite3 import Error
from typing import List, Dict, Optional
from pydantic import BaseModel
import json



class CreateCampaign(BaseModel):
    title: str
    description: str
    character_classes: List[str]
    character_types: List[str]


class Campaign(CreateCampaign):
    id: int


class CreateCharacter(BaseModel):
    campaign_id: int
    name: Optional[str]
    character_class: str
    character_type: str
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
    sql = """INSERT INTO campaigns(title, description, character_classes, character_types) VALUES(?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(
        sql, (campaign.title, campaign.description, json.dumps(campaign.character_classes), json.dumps(campaign.character_types))
    )
    conn.commit()
    return cur.lastrowid


def get_campaign(id: int, conn: sqlite3.Connection) -> Campaign:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, character_classes, character_types FROM campaigns WHERE id = ?",
        (id,),
    )
    row = cur.fetchone()
    return _parse_campaign(row)


def _parse_campaign(row: sqlite3.Row) -> Campaign:
    return Campaign.parse_obj(
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "character_classes": json.loads(row[3]),
            "character_types": json.loads(row[4]),
        }
    )


def get_campaigns(conn: sqlite3.Connection) -> List[Campaign]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, character_classes, character_types FROM campaigns"
    )
    rows = cur.fetchall()
    return [_parse_campaign(row) for row in rows]


def delete_campaign(id: int, conn: sqlite3.Connection) -> None:
    sql = "DELETE FROM campaigns WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def create_character(character: CreateCharacter, conn: sqlite3.Connection) -> int:
    sql = """INSERT INTO characters(campaign_id, name, character_class, character_type, backstory, attributes, primary_goal, inventory) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(
        sql,
        (
            character.campaign_id,
            character.name,
            character.character_class,
            character.character_type,
            character.backstory,
            json.dumps(character.attributes),
            character.primary_goal,
            json.dumps(character.inventory),
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_characters(campaign_id: int, conn: sqlite3.Connection) -> List[Character]:
    cur = conn.cursor()
    cur.execute("SELECT id, name, campaign_id, character_class, character_type, backstory, attributes, primary_goal, inventory FROM characters WHERE campaign_id = ?", (campaign_id,))
    rows = cur.fetchall()
    return [
        Character(
            id=row[0],
            name=row[1],
            campaign_id=row[2],
            character_class=row[3],
            character_type=row[4],
            backstory=row[5],
            attributes=json.loads(row[6]),
            primary_goal=row[7],
            inventory=json.loads(row[8]),
        )
        for row in rows
    ]


def update_character(character: Character, conn: sqlite3.Connection) -> None:
    sql = """UPDATE characters SET name = ?, charactoer_class = ?, charactoer_type = ?, backstory = ?, attributes = ?, primary_goal = ?, inventory = ? WHERE id = ?"""
    cur = conn.cursor()
    cur.execute(
        sql,
        (
            character.name,
            character.character_class,
            character.character_type,
            character.backstory,
            json.dumps(character.attributes),
            character.primary_goal,
            json.dumps(character.inventory),
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
                                        title TEXT NOT NULL,
                                        description TEXT NOT NULL,
                                        character_classes TEXT NOT NULL,
                                        character_types TEXT NOT NULL
                                    );"""

    sql_create_characters_table: str = """CREATE TABLE IF NOT EXISTS characters (
                                        id INTEGER PRIMARY KEY,
                                        campaign_id INTEGER NOT NULL,
                                        name TEXt,
                                        character_class TEXT NOT NULL,
                                        character_type TEXT NOT NULL,
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
