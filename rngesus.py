import json
import os
import random
from typing import List

import guidance
import openai
from database import Campaign, Character

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# set the default language model used to execute guidance programs
guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")


def prompt(question: str) -> str:
    print(f"requesting question '{question}'")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}]
    )
    print(f"response: {response.choices[0].message.content}")
    return response.choices[0].message.content



gen_char = guidance(
'''
{{#system~}}
You are the dungeon master of an RPG game.

This is the description of the game:
"""
{{description}}
"""

Where the rules are undefined, you must make them up. You invented this game!

Now you are the dungeon master. Make the game challenging, exciting, and rewarding!

Take advantage of the games unique mechanics, and tell a really good story.
{{/system~}}
{{#user~}}
Generate me a new character. The character has the class of {{character_class}} and the role of {{character_type}}.
{{/user~}}
{{#user~}}
First, what's the character's name? Respond concisely with just the name. For example: "Max Ernst"
{{/user~}}
{{#assistant~}}
{{gen 'name' max_tokens=20 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Now, give the user an exciting backstory. Make me want to play this character!
{{/user~}}
{{#assistant~}}
{{gen 'backstory' max_tokens=200 temperature=0.9}}
{{/assistant~}}
{{#user~}}
Concisely in a single sentence, what's the characters primary story goal? 
{{/user~}}
{{#assistant~}}
{{gen 'primary_goal' max_tokens=100 temperature=0.9}}
{{/assistant~}}
{{#user~}}
Now, assign attribute scores between 1 and 20 (inclusive) for all attributes: {{attributes}}

Respond as a comma delimited list with colons indicating the attributes score. Use no other punctuation.

This is the format: "Attribute Name: Score, Another Attribute Name: Score"

For example:
Influence: 18, Power: 12,

{{/user~}}
{{#assistant~}}
{{gen 'attributes' max_tokens=50 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Now, list the inventory as a comma delimited list. Don't give me too many things, I need to save room for later acquisitions!
Focus on the essentials that my character in their role needs to play.
Respond with just the items separated by commas. For example: "Water Bottle, Sword, Potion"
{{/user~}}
{{#assistant~}}
{{gen 'inventory' max_tokens=100 temperature=0.1}}
{{/assistant~}}
'''
)


def roll_character(campaign: Campaign) -> Character:
    character_class = random.choice(campaign.character_classes)
    character_type = random.choice(campaign.character_types)
    program = gen_char(
        description=campaign.summary,
        attributes=", ".join(campaign.attributes),
        character_class=character_class,
        character_type=character_type,
    )

    attributes = [xs.split(": ") for xs in program["attributes"].split(",")]
    attributes = {
        (k.strip()): int("".join(filter(str.isdigit, v))) for [k, v] in attributes
    }
    return Character(
        name=program["name"],
        campaign_id=campaign.id,
        character_class=program["character_class"],
        character_type=program["character_type"],
        backstory=program["backstory"],
        attributes=attributes,
        primary_goal=program["primary_goal"],
        inventory=program["inventory"].split(", "),
    )


gen_campaign = guidance(
    '''
{{#system~}}
You are an author of RPG games.

You love doing this! You think deeply about games.
You love imagining new game worlds to explore, inventing story intrigue. You have limitless imagination!

You love coming up with new game mechanics! Who wants to play the same game again? You like to re-invent the genre.
{{/system~}}
{{#user~}}
Create a game according to this premise:

"""
{{prompt}}
"""

First, give the game an exciting title!
{{~/user~}}
{{~#assistant~}}
{{gen 'title' temperature=1 max_tokens=20}}
{{~/assistant~}}
{{~#user~}}
Give us a quick elevator pitch!
{{~/user~}}
{{~#assistant~}}
{{gen 'description' temperature=1}}
{{~/assistant~}}
{{~#user~}}
Does the game have any character classes?
Respond with ONLY a comma delimited list of the the character class names. 
Respond with between 1 and 8 classes.
For example: "Attorney, Designer, Janitor"
{{~/user~}}
{{~#assistant~}}
{{gen 'character_classes' max_tokens=30 temperature=0.3}}
{{~/assistant~}}
{{#user~}}
Who are the types of people in this story and where do they come from? Describe the socio-ethnic types in the game. Whatever fits the story. 
Think outside of the box!
Respond with between 1 and 8 types.
Respond with ONLY a comma delimited list of the types. 
For example: "Human, Half-Alien, Sentient Printer"
{{/user~}}
{{#assistant~}}
{{gen 'character_types' max_tokens=30 temperature=0.3}}
{{/assistant~}}
{{#user~}}
What are the attributes in the game? Whatever fits the story.
Respond with only a comma delimited list of attribute names.
Respond with between 1 and 8 attributes.
For example: "Power, Influence, Magic, Luck, Flexibility"
{{/user~}}
{{#assistant~}}
{{gen 'character_attributes' max_tokens=50 temperature=0.3}}
{{/assistant~}}
{{#user~}}
What's the hook. Tell me about the game world, and the story intrigue.
Get specific. Tell me details about how the story starts: an intriguing scene or incident.
{{/user~}}
{{#assistant~}}
{{gen 'story' temperature=0.9}}
{{/assistant~}}
{{#user~}}
What are the mechanics? I want to know what makes this game unique from other RPGs! 

Get specific. How do players affect the game?
Feel free to make up new rules that go beyond the standards of the genre.
{{/user~}}
{{#assistant~}}
{{gen 'mechanics' temperature=0.9}}
{{/assistant~}}
{{#geneach 'mechanics_continued' num_iterations=3}}
{{#user~}}
continue
{{/user~}}
{{#assistant~}}
{{gen 'this' temperature=0.9}}
{{/assistant~}}
{{/geneach}}
{{#user~}}
You will need a reminder for yourself to remember what this game is about and how the game works.
Write a paragraph of the things that you might forget, (title, setting, story, mechanics)
{{/user~}}
{{#assistant~}}
{{gen 'summary' temperature=0.9}}
{{/assistant~}}
'''
)


def generate_campaign_raw(prompt: str) -> guidance.Program:
    # TODO - figure out some mechanism to stream the campaign to the UI with async mode
    return gen_campaign(
        prompt=prompt, class_count=2, type_count=2, attribute_count=2, async_mode=False
    )


def generate_campaign(prompt: str) -> Campaign:
    generated = generate_campaign_raw(prompt)
    return Campaign(
        title=generated["title"].replace('"', ""),
        description=generated["description"].replace('"', "")
        + "\n"
        + generated["story"]
        + "\n"
        + generated["mechanics"]
        + "\n"
        + "\n".join(generated["mechanics_continued"]),
        summary=generated["summary"],
        character_classes=generated["character_classes"].split(", "),
        character_types=generated["character_types"].split(", "),
        attributes=generated["character_attributes"].split(", "),
    )


def generate_character_backstory():
    return prompt("Generate a character backstory for an RPG game")


def generate_attribute_scores():
    scores = prompt("Generate a set of 6 attribute scores for an RPG character")
    return [int(score) for score in scores.split(",")]


def generate_primary_goal():
    return prompt("Generate a primary goal for an RPG character")


def generate_inventory_items():
    items = prompt("Generate a list of inventory items for an RPG character")
    return items.split(",")


def generate_campaign_concept(context):
    return prompt(f"Generate a concept for an RPG game set in {context}")


def generate_scene_description():
    return prompt("Generate a scene description for an RPG game")


def generate_ai_response(player_action):
    return prompt(
        f"AI Dungeon Master, how do you respond to the player's action: {player_action}"
    )
