from typing import AsyncIterator, List, TypeVar

from fastapi import status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic.generics import GenericModel, Generic

from . import game
from .app import app
from .models import Campaign, Character

DataT = TypeVar("DataT")


class CreateCampaign(BaseModel):
    description: str


class ListResponse(GenericModel, Generic[DataT]):
    items: List[DataT]


class GenericResponse(BaseModel):
    status: str


##########################
## Campaigns
@app.get("/api/campaigns", response_model=ListResponse)
def get_campaigns() -> ListResponse:
    return ListResponse(items=game.get_campaign_summaries())


@app.post("/api/campaigns", response_class=StreamingResponse)
async def create_campaign(request: CreateCampaign) -> StreamingResponse:
    return StreamingResponse(
        content=generate_nd_json(game.generate_campaign(request.description)),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )


async def generate_nd_json(iterator: AsyncIterator[BaseModel]) -> AsyncIterator[str]:
    async for c in iterator:
        yield c.json() + "\n"


@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: int) -> Campaign:
    camp = game.get_campaign(campaign_id)
    if camp is None:
        return "Campaign not found", status.HTTP_404_NOT_FOUND
    return camp


##########################
## Characters
@app.get("/api/characters", response_model=ListResponse)
def get_characters(campaign_id: int) -> ListResponse:
    return ListResponse(items=game.get_character_summaries(campaign_id))


@app.post("/api/characters", response_class=StreamingResponse)
async def roll_character(campaign_id: int) -> StreamingResponse:
    result = await game.add_character(campaign_id)
    if result is None:
        return "Campaign not found", status.HTTP_404_NOT_FOUND
    return StreamingResponse(
        content=generate_nd_json(result),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )


@app.get("/api/characters/{character_id}", response_model=Character)
def get_character(character_id: int) -> Character:
    char = game.get_character(character_id)
    if char is None:
        return "Character not found", status.HTTP_404_NOT_FOUND
    return char


@app.delete("/api/characters/{character_id}", response_model=GenericResponse)
def delete_character(character_id: int) -> GenericResponse:
    deleted = game.delete_character(character_id)
    return GenericResponse(status="deleted" if deleted else "no_match")


##########################
## Chat


@app.get("/api/chats", response_model=ListResponse)
def get_chats(campaign_id: int) -> ListResponse:
    return ListResponse(items=game.load_chats(campaign_id))


@app.put("/api/campaigns/{campaign_id}/chat", response_class=StreamingResponse)
def chat_resume(campaign_id: int, user_message: str | None = None) -> StreamingResponse:
    return StreamingResponse(
        content=generate_nd_json(
            game.assistant_generate(campaign_id)
            if user_message is None
            else game.user_respond(campaign_id, user_message)
        ),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )
