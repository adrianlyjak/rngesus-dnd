import datetime
import time
from typing import AsyncIterator, List

from fastapi import status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from . import database, rngesus
from .app import app
from .models import Campaign, CampaignSummary, Character, CharacterSummary, Chat


## Campaign CRUD ##
def get_campaign_summaries() -> List[CampaignSummary]:
    return database.get_campaign_summaries()

def get_active_characters(campaign_id: int) -> List[Character]:
    return database.get_active_characters_in_campaign(campaign_id)


def get_campaign(campaign_id: int) -> Campaign | None:
    return database.get_campaign(campaign_id)


async def regenerate_campaign(campaign: Campaign) -> AsyncIterator[Campaign]:
    program = rngesus.generate_campaign(campaign, update_frequency_seconds=1)
    async for generated in program:
        database.upsert_campaign(generated)
        yield campaign


async def generate_campaign(description: str) -> AsyncIterator[Campaign]:
    campaign = None
    program = rngesus.generate_new_campaign(description, update_frequency_seconds=1)
    async for generated in program:
        if campaign is None:
            campaign = database.upsert_campaign(generated)
        else:
            generated.id = campaign.id
            database.upsert_campaign(generated)
            campaign = generated
        yield campaign


## Character CRUD ##


def get_character_summaries(campaign_id: int) -> List[CharacterSummary]:
    return database.get_character_summaries(campaign_id)


async def add_character(campaign_id: int) -> None | AsyncIterator[Character]:
    campaign = database.get_campaign(campaign_id)
    characters = database.get_character_summaries(campaign_id)
    if campaign is None:
        return None
    else:
        return _generate_character(campaign, characters)
    
def activate_character(character_id: int) -> None:
    database.activate_character(character_id, time.time_ns() // 1000000)

def deactivate_character(character_id: int) -> None:
    database.deactivate_character(character_id)

def get_character(character_id: int) -> Character | None:
    return database.get_character(character_id)


def delete_character(character_id: int) -> bool:
    return database.delete_character(character_id)


async def _generate_character(campaign: Campaign, characters: List[CharacterSummary]) -> AsyncIterator[Character]:
    char = None
    async for c in rngesus.roll_character(campaign, characters):
        char = c
        yield char
    if char is not None:
        char = database.upsert_character(char)
        yield char


## Chat ##


class ChatState(BaseModel):
    campaign: Campaign
    characters: List[Character]
    dialog: List[Chat]


def load_chats(campaign_id: int) -> List[Chat]:
    return database.get_chat_history(campaign_id)


def load_chat_state(campaign_id: int) -> ChatState:
    camp = database.get_campaign(campaign_id)
    characters = database.get_active_characters_in_campaign(campaign_id)
    dialog = database.get_chat_history(campaign_id)
    return ChatState(campaign=camp, characters=characters, dialog=dialog)


async def assistant_generate(campaign_id: int) -> AsyncIterator[Chat]:
    state = load_chat_state(campaign_id)
    assistant: Chat | None = None
    async for resp in rngesus.generate_chat(
        state.campaign, state.characters, state.dialog
    ):
        if state.campaign.scenario != resp.scenario and resp.scenario:
            print(f"resp.scenario '{resp.scenario}' {type(resp.scenario)}")
            state.campaign.scenario = resp.scenario
            print("camp " + str(state.campaign))
            print(state.campaign.scenario)
            database.upsert_campaign(state.campaign)
        print(resp.scenario, resp.assistant)
        if resp.assistant:
            if not assistant:
                assistant = Chat(
                    campaign_id=campaign_id,
                    user_type="assistant",
                    message=resp.assistant,
                )
            assistant.message = resp.assistant
            database.upsert_chat_message(assistant)
            yield assistant


def user_respond(campaign_id: int, message: str) -> AsyncIterator[Chat]:
    database.upsert_chat_message(
        Chat(campaign_id=campaign_id, user_type="user", message=message)
    )
    return assistant_generate(campaign_id)
