from dotenv import load_dotenv

load_dotenv()

from functools import wraps
from typing import List, Optional, Tuple

import database
import rngesus
from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def landing_page() -> str:
    return render_template("landing_page.html")


@app.route("/game", methods=["GET", "POST"])
def game_screen() -> str:
    if request.method == "POST":
        return redirect(url_for("new_campaign"))
    campaigns = database.get_campaigns()
    return render_template("game_screen.html", campaigns=campaigns)


@app.route("/new_campaign", methods=["GET", "POST"])
def new_campaign() -> str:
    if request.method == "POST":
        description: Optional[str] = request.form["campaign_description"]
        if description:
            create = rngesus.generate_campaign(description)
            id = database.create_campaign(create)
            return redirect(url_for("character_list", campaign_id=id))
    return render_template("new_campaign.html")


@app.route("/character_list/<int:campaign_id>", methods=["GET", "POST"])
def character_list(campaign_id: int) -> str:
    if request.method == "POST":
        return redirect(url_for("character_creation", campaign_id=campaign_id))
    campaign = database.get_campaign(campaign_id)
    characters = database.get_characters(campaign_id)
    return render_template("character_list.html", characters=characters, campaign=campaign)


@app.route("/api/roll_character/<int:campaign_id>")
def roll_character(campaign_id: int) -> str:
    camp = database.get_campaign(campaign_id)
    if camp is None:
        return "Campaign not found", 404
    return rngesus.roll_character(camp).json()


@app.route("/character_creation/<int:campaign_id>", methods=["GET", "POST"])
def character_creation(campaign_id: int) -> str:
    print(request.method)
    if request.method == "POST":
        character = CreateCharacter.parse_raw(request.form["character"])
        database.create_character(character)
        return redirect(url_for("character_list", campaign_id=campaign_id))
    return render_template("character_creation.html")


@app.route("/play/<int:campaign_id>")
def play_screen(campaign_id: int) -> str:
    chat_history = database.get_chat_history(campaign_id)
    return render_template("play_screen.html", chat_history=chat_history)


if __name__ == "__main__":
    database.main()
    app.run(debug=True, port=5001)
