from typing import List, Dict, Optional
from sqlmodel import JSON, Column, SQLModel, Field, create_engine, Session
from pydantic import BaseModel


engine = create_engine("sqlite:///rngesus.db")



class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    summary: str
    character_classes: List[str] = Field(sa_column=Column(JSON))
    character_types: List[str] = Field(sa_column=Column(JSON))
    attributes: List[str] = Field(sa_column=Column(JSON))


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int
    name: Optional[str]
    character_class: str
    character_type: str
    backstory: str
    attributes: Dict[str, int] = Field(sa_column=Column(JSON))
    primary_goal: str
    inventory: List[str] = Field(sa_column=Column(JSON))


class ChatMessage(BaseModel):
    campaign_id: int
    user_type: str
    message: str


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int
    user_type: str
    message: str


def upsert_campaign(campaign: Campaign) -> Campaign:
    with Session(engine) as session:
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
    return campaign


def get_campaign(id: int) -> Optional[Campaign]:
    with Session(engine) as session:
        campaign = session.get(Campaign, id)
        return campaign


def get_campaigns() -> List[Campaign]:
    with Session(engine) as session:
        campaigns = session.query(Campaign).all()
        return campaigns


def delete_campaign(id: int) -> None:
    with Session(engine) as session:
        campaign = session.get(Campaign, id)
        session.delete(campaign)
        session.commit()


def create_character(character: Character) -> Character:
    with Session(engine) as session:
        session.add(character)
        session.commit()
        session.refresh(character)
    return character


def get_characters(campaign_id: int) -> List[Character]:
    with Session(engine) as session:
        characters = session.query(Character).filter(Character.campaign_id == campaign_id).all()
        return characters


def update_character(character: Character) -> None:
    with Session(engine) as session:
        session.add(character)
        session.commit()


def delete_character(id: int) -> None:
    with Session(engine) as session:
        character = session.get(Character, id)
        session.delete(character)
        session.commit()


def add_chat_message(chat_message: ChatMessage) -> int:
    chat_obj = Chat.from_orm(chat_message)
    with Session(engine) as session:
        session.add(chat_obj)
        session.commit()
        session.refresh(chat_obj)
    return chat_obj.id


def get_chat_history(campaign_id: int) -> List[ChatMessage]:
    with Session(engine) as session:
        chat_messages = session.query(Chat).filter(Chat.campaign_id == campaign_id).all()
        return [ChatMessage.from_orm(chat) for chat in chat_messages]


def main() -> None:
    SQLModel.metadata.create_all(engine)

