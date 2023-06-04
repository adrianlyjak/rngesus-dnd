from typing import AsyncIterator, List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import status

from .models import Campaign, CampaignSummary, Character, CharacterSummary
from .app import app
from . import database, rngesus


class CreateCampaign(BaseModel):
    description: str


class CampaignSummaryList(BaseModel):
    campaigns: List[CampaignSummary]


class CharacterSummaryList(BaseModel):
    characters: List[CharacterSummary]

class GenericResponse(BaseModel):
    status: str


@app.get("/api/campaigns", response_model=CampaignSummaryList)
def get_campaigns() -> CampaignSummaryList:
    return CampaignSummaryList(campaigns=database.get_campaign_summaries())


@app.post("/api/campaigns", response_class=StreamingResponse)
async def create_campaign(request: CreateCampaign) -> StreamingResponse:
    return StreamingResponse(
        content=generate_campaign_ndjson(request),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )


async def generate_campaign(request: CreateCampaign) -> AsyncIterator[CreateCampaign]:
    campaign = None
    program = rngesus.generate_campaign(request.description, update_frequency_seconds=1)
    async for generated in program:
        if campaign is None:
            campaign = database.upsert_campaign(generated)
        else:
            generated.id = campaign.id
            database.upsert_campaign(generated)
            campaign = generated
        yield campaign


async def generate_campaign_ndjson(request: CreateCampaign) -> AsyncIterator[str]:
    async for c in generate_campaign(request):
        yield c.json() + "\n"


@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: int) -> Campaign:
    return database.get_campaign(campaign_id)


@app.get("/api/characters", response_model=CharacterSummaryList)
def get_characters(campaign_id: int) -> CharacterSummaryList:
    return CharacterSummaryList(
        characters=database.get_character_summaries(campaign_id)
    )


@app.post("/api/characters", response_class=StreamingResponse)
async def roll_character(campaign_id: int) -> StreamingResponse:
    campaign = database.get_campaign(campaign_id)
    if campaign is None:
        return "Campaign not found", status.HTTP_404_NOT_FOUND
    return StreamingResponse(
        content=generate_character_ndjson(campaign),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )


@app.get("/api/characters/{character_id}", response_model=Character)
def get_character(campaign_id: int, character_id: int) -> Character:
    char = database.get_character(character_id)
    if char is None:
        return "Character not found", status.HTTP_404_NOT_FOUND
    return char

@app.delete("/api/characters/{character_id}", response_model=GenericResponse)
def delete_character(character_id: int) -> GenericResponse:
    deleted = database.delete_character(character_id)
    return GenericResponse(status="deleted" if deleted else "no_match")

async def generate_character(campaign: Campaign) -> AsyncIterator[Character]:
    char = None
    async for c in rngesus.roll_character(campaign):
        if char is not None:
            c.id = char.id
        char = database.upsert_character(c)
        yield char


async def generate_character_ndjson(campaign_id: int) -> AsyncIterator[str]:
    async for c in generate_character(campaign_id):
        yield c.json() + "\n"
