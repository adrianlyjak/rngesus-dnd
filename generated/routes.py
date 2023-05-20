from flask import Flask, render_template, request, redirect, url_for
import database
from database import CreateCampaign
import rngesus
from typing import Optional

app = Flask(__name__)


@app.route("/")
def landing_page():
    return render_template("landing.html")


@app.route("/game")
def game_screen():
    campaigns = database.get_campaigns()
    return render_template("game.html", campaigns=campaigns)



# @app.route('/character_list')
# def character_list():
#     characters = database.get_characters()
#     return render_template('character_list.html', characters=characters)


@app.route("/character_creation", methods=["GET", "POST"])
def character_creation():
    if request.method == "POST":
        character_data = rngesus.prompt("Generate a new character")
        database.create_character(character_data)
        return redirect(url_for("character_list"))
    return render_template("character_creation.html")


@app.route("/play/<int:campaign_id>")
def play_screen(campaign_id):
    chat_history = database.get_chat_history(campaign_id)
    return render_template("play.html", chat_history=chat_history)


@app.route("/send_message", methods=["POST"])
def send_message():
    campaign_id = request.form["campaign_id"]
    message = request.form["message"]
    database.add_chat_message(campaign_id, "player", message)
    ai_response = rngesus.prompt(message)
    database.add_chat_message(campaign_id, "ai", ai_response)
    return redirect(url_for("play_screen", campaign_id=campaign_id))


if __name__ == "__main__":
    app.run(debug=True)
