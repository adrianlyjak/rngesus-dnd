from flask import Flask, render_template, request, redirect, url_for
import database
import rngesus

app = Flask(__name__)

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/game', methods=['GET', 'POST'])
def game_screen():
    if request.method == 'POST':
        return redirect(url_for('new_campaign'))
    campaigns = database.get_campaigns()
    return render_template('game_screen.html', campaigns=campaigns)

@app.route('/new_campaign', methods=['GET', 'POST'])
def new_campaign():
    if request.method == 'POST':
        description = request.form['campaign_description']
        if description:
            database.create_campaign(description)
            return redirect(url_for('character_list'))
    return render_template('new_campaign.html')

@app.route('/character_list', methods=['GET', 'POST'])
def character_list():
    if request.method == 'POST':
        return redirect(url_for('character_creation'))
    characters = database.get_characters()
    return render_template('character_list.html', characters=characters)

@app.route('/character_creation', methods=['GET', 'POST'])
def character_creation():
    if request.method == 'POST':
        character = rngesus.roll_character()
        database.create_character(character)
        return redirect(url_for('character_list'))
    return render_template('character_creation.html')

@app.route('/play/<int:campaign_id>')
def play_screen(campaign_id):
    chat_history = database.get_chat_history(campaign_id)
    return render_template('play_screen.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)