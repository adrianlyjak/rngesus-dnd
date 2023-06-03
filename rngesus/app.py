from dotenv import load_dotenv

from .models import Campaign, Character

load_dotenv()

from typing import Annotated, AsyncIterator, List

from fastapi import FastAPI, Form, Request, responses, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from . import rngesus

from . import database

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount the static files at the /static endpoint
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request) -> str:
    return templates.TemplateResponse("landing_page.html", {"request": request})


@app.get("/game", response_class=HTMLResponse)
async def game_screen(request: Request) -> str:
    campaigns = database.get_campaigns()
    return templates.TemplateResponse(
        "game_screen.html", {"request": request, "campaigns": campaigns}
    )


class CreateCampaign(BaseModel):
    description: str


@app.post("/new_campaign", response_class=responses.RedirectResponse)
async def new_campaign(campaign_description: Annotated[str, Form()]) -> str:
    print(campaign_description)
    create = rngesus.generate_campaign(campaign_description)
    campaign = database.upsert_campaign(create)
    return RedirectResponse(
        f"/character_list/{campaign.id}", status_code=status.HTTP_302_FOUND
    )


@app.post("/campaigns", response_class=StreamingResponse)
async def create_campaign(request: CreateCampaign) -> StreamingResponse:
    return StreamingResponse(
        content=generate_campaign_ndjson(request),
        status_code=status.HTTP_200_OK,
        media_type="application/ndjson",
    )


async def generate_campaign(request: CreateCampaign) -> AsyncIterator[CreateCampaign]:
    campaign = None
    program = rngesus.generate_campaign(request.description)
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

@app.get("/new_campaign", response_class=HTMLResponse)
async def create_campaign(request: Request) -> str:
    return templates.TemplateResponse("new_campaign.html", {"request": request})


@app.get("/character_list/{campaign_id}", response_class=HTMLResponse)
async def character_list(request: Request, campaign_id: int) -> str:
    campaign = database.get_campaign(campaign_id)
    characters = database.get_characters(campaign_id)
    return templates.TemplateResponse(
        "character_list.html",
        {"request": request, "characters": characters, "campaign": campaign},
    )


@app.get("/api/roll_character/{campaign_id}", response_class=Character)
async def roll_character(campaign_id: int) -> str:
    camp = database.get_campaign(campaign_id)
    if camp is None:
        return "Campaign not found", status.HTTP_404_NOT_FOUND
    return rngesus.roll_character(camp)


@app.get("/character_creation/{campaign_id}", response_class=HTMLResponse)
async def character_creation(request: Request, campaign_id: int) -> str:
    return templates.TemplateResponse("character_creation.html", {"request": request})


@app.post(
    "/character_creation/{campaign_id}", response_class=responses.RedirectResponse
)
async def create_character(campaign_id: int, character: str = Form(...)) -> str:
    character = rngesus.CreateCharacter.parse_raw(character)
    database.create_character(character)
    return f"/character_list/{campaign_id}"


@app.get("/play/{campaign_id}", response_class=HTMLResponse)
async def play_screen(request: Request, campaign_id: int) -> str:
    chat_history = database.get_chat_history(campaign_id)
    return templates.TemplateResponse(
        "play_screen.html", {"request": request, "chat_history": chat_history}
    )

@app.on_event("startup")
def on_startup():
    database.main()