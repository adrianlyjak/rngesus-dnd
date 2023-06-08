from typing import Dict, List, Optional

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Session, SQLModel, create_engine, select

from .models import (
    Campaign,
    CampaignSummary,
    CampaignSummaryTuple,
    Character,
    CharacterSummary,
    CharacterSummaryTuple,
    Chat,
    campaign_summary,
    character_summary,
)

engine = create_engine("sqlite:///rngesus.db", echo=True)


def upsert_campaign(campaign: Campaign) -> Campaign:
    with Session(engine) as session:
        if campaign.id:
            session.query(Campaign).filter(Campaign.id == campaign.id).update(
                campaign.dict()
            )
            session.commit()
        else:
            session.add(campaign)
            session.commit()
            session.refresh(campaign)
    return campaign


def get_campaign(id: int) -> Optional[Campaign]:
    with Session(engine) as session:
        campaign = session.get(Campaign, id)
        return campaign


def get_campaign_summaries() -> List[CampaignSummary]:
    with Session(engine) as session:
        campaigns = session.exec(select(*CampaignSummaryTuple)).all()
        return [campaign_summary(tuple) for tuple in campaigns]


def delete_campaign(id: int) -> None:
    with Session(engine) as session:
        campaign = session.get(Campaign, id)
        session.delete(campaign)
        session.commit()


def upsert_character(character: Character) -> Character:
    with Session(engine) as session:
        if character.id:
            session.query(Character).filter(Character.id == character.id).update(
                character.dict()
            )
            session.commit()
        else:
            session.add(character)
            session.commit()
            session.refresh(character)
    return character


def get_character_summaries(campaign_id: int) -> List[CharacterSummary]:
    with Session(engine) as session:
        tuples = (
            session.query(*CharacterSummaryTuple)
            .filter(Character.campaign_id == campaign_id)
            .all()
        )
        return [character_summary(tuple) for tuple in tuples]


def get_characters_in_campaign(campaign_id: int) -> List[Character]:
    with Session(engine) as session:
        characters = (
            session.query(Character).filter(Character.campaign_id == campaign_id).all()
        )
        return characters


def get_character(id: int) -> Optional[Character]:
    with Session(engine) as session:
        character = session.get(Character, id)
        return character


def delete_character(id: int) -> bool:
    with Session(engine) as session:
        count = session.query(Character).filter(Character.id == id).delete()
        session.commit()
        return count > 0


def upsert_chat_message(chat: Chat) -> Chat:
    with Session(engine) as session:
        if chat.id:
            session.query(Campaign).filter(Campaign.id == chat.id).update(chat.dict())
            session.commit()
        else:
            session.add(chat)
            session.commit()
            session.refresh(chat)
    return chat


def get_chat_history(campaign_id: int) -> List[Chat]:
    with Session(engine) as session:
        chat_messages = (
            session.query(Chat)
            .filter(Chat.campaign_id == campaign_id)
            .order_by(Chat.id)
            .all()
        )
        return chat_messages


def main() -> None:
    SQLModel.metadata.create_all(engine)
