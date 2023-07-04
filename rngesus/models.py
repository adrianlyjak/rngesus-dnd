import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

from sqlmodel import JSON, Column, Field, SQLModel


class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str = ''
    title: str = ''
    description: str = ''
    summary: Optional[str] = ''
    character_classes: List[str] = Field(sa_column=Column(JSON), default=[])
    character_types: List[str] = Field(sa_column=Column(JSON), default=[])
    attributes: List[str] = Field(sa_column=Column(JSON), default=[])
    scenario: str = ""

CampaignSummaryTuple = [Campaign.id, Campaign.title, Campaign.summary]

# projection of campaign
class CampaignSummary(BaseModel):
    id: int
    title: str
    summary: Optional[str] = ''

def campaign_summary(tuple: Tuple[int, str, str]) -> CampaignSummary:
    return CampaignSummary(id=tuple[0], title=tuple[1], summary=tuple[2])


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # is_selected: bool
    campaign_id: int
    name: Optional[str]
    character_class: str
    character_type: str
    backstory: str
    attributes: Dict[str, int] = Field(sa_column=Column(JSON))
    primary_goal: str
    inventory: List[str] = Field(sa_column=Column(JSON))
    activated: Optional[int]


CharacterSummaryTuple = [
    Character.id,
    Character.name,
    Character.character_class,
    Character.character_type,
]


class CharacterSummary(BaseModel):
    id: int
    name: str
    character_class: str
    character_type: str


def character_summary(tuple: Tuple[int, str, str, str]) -> CharacterSummary:
    return CharacterSummary(
        id=tuple[0], name=tuple[1], character_class=tuple[2], character_type=tuple[3]
    )


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int
    user_type: str
    message: str
