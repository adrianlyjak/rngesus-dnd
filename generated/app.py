from dotenv import load_dotenv

load_dotenv()

from database import CreateCampaign
from typing import List, Optional, Tuple
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, g
import database
import rngesus
import sqlite3
import os

app = Flask(__name__)


# Define the types of the return values for the functions
def get_db_conn() -> sqlite3.Connection:
    return getattr(g, "_db_conn", None)


def with_db_conn(f: callable) -> callable:
    @wraps(f)
    def wrapped(*args, **kwargs) -> any:
        # Check if a connection exists in Flask's g object
        if get_db_conn() is None:
            # If no connection, obtain one from the connection pool
            g._db_conn = database.create_connection()
        # Call the route function with the connection as an argument
        return f(*args, db_conn=get_db_conn(), **kwargs)

    return wrapped


@app.route("/")
def landing_page() -> str:
    return render_template("landing_page.html")


@app.route("/game", methods=["GET", "POST"])
@with_db_conn
def game_screen(db_conn: sqlite3.Connection) -> str:
    if request.method == "POST":
        return redirect(url_for("new_campaign"))
    campaigns = database.get_campaigns(db_conn)
    return render_template("game_screen.html", campaigns=campaigns)


@app.route("/new_campaign", methods=["GET", "POST"])
@with_db_conn
def new_campaign(db_conn: sqlite3.Connection) -> str:
    if request.method == "POST":
        description: Optional[str] = request.form["campaign_description"]
        if description:
            types = rngesus.generate_character_types()
            roles = rngesus.generate_character_roles()
            id = database.create_campaign(
                CreateCampaign(
                    description=description,
                    character_roles=roles,
                    character_types=types,
                ),
                db_conn,
            )
            return redirect(url_for("character_list", campaign_id=id))
    return render_template("new_campaign.html")


@app.route("/character_list/<int:campaign_id>", methods=["GET", "POST"])
@with_db_conn
def character_list(campaign_id: int, db_conn: sqlite3.Connection) -> str:
    if request.method == "POST":
        return redirect(url_for("character_creation"))
    characters = database.get_characters(campaign_id, db_conn)
    return render_template("character_list.html", characters=characters)


@app.route("/api/roll_character/<int:campaign_id>")
@with_db_conn
def roll_character(campaign_id: int, db_conn: sqlite3.Connection) -> str:
    camp = database.get_campaign(campaign_id, db_conn)
    if camp is None:
        return "Campaign not found", 404
    return rngesus.roll_character(camp).json()


@app.route("/character_creation", methods=["GET", "POST"])
@with_db_conn
def character_creation(db_conn: sqlite3.Connection) -> str:
    if request.method == "POST":
        character = rngesus.roll_character()
        database.create_character(character, db_conn)
        return redirect(url_for("character_list"))
    return render_template("character_creation.html")


@app.route("/play/<int:campaign_id>")
def play_screen(campaign_id: int, db_conn: sqlite3.Connection) -> str:
    chat_history = database.get_chat_history(campaign_id, db_conn)
    return render_template("play_screen.html", chat_history=chat_history)


if __name__ == "__main__":
    database.main()
    app.run(debug=True)
