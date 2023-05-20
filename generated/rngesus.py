import openai
import os

# TODO - refactor to use guidance library, and suggest interdependencies and templates for making the 
# prompts more complex

# TODO - use dotenv to load environment variables

openai.api_key = os.environ["OPENAI_API_KEY"]

def prompt(question):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=question,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

def generate_character_role():
    return prompt("Generate a random character role for an RPG game")

def generate_character_type():
    return prompt("Generate a random character type for an RPG game")

def generate_character_backstory():
    return prompt("Generate a character backstory for an RPG game")

def generate_attribute_scores():
    scores = prompt("Generate a set of 6 attribute scores for an RPG character")
    return [int(score) for score in scores.split(',')]

def generate_primary_goal():
    return prompt("Generate a primary goal for an RPG character")

def generate_inventory_items():
    items = prompt("Generate a list of inventory items for an RPG character")
    return items.split(',')

def generate_campaign_concept(context):
    return prompt(f"Generate a concept for an RPG game set in {context}")

def generate_scene_description():
    return prompt("Generate a scene description for an RPG game")

def generate_ai_response(player_action):
    return prompt(f"AI Dungeon Master, how do you respond to the player's action: {player_action}")