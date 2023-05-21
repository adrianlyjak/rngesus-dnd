import json
import os
import random
from typing import List

import guidance
import openai
from database import Campaign, CreateCampaign, CreateCharacter

# TODO - refactor to use guidance library, and suggest interdependencies and templates for making the
# prompts more complex

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


default_attributes = [
    "Strength",
    "Dexterity",
    "Constitution",
    "Intelligence",
    "Wisdom",
    "Charisma",
]


def campaign_description(campaign: Campaign):
    f"""
    This is the description of the game:
    {campaign.description}

    These are some of the available character configurations for the game:
    Classes: {', '.join(campaign.character_classes)}
    Roles: {', '.join(campaign.character_classes)}
    Attributes: {', '.join(default_attributes)}
    """


gen_char = guidance(
    """
{{#system~}}
You are the dungeon master of an RPG game called {{title}}.

This is the description of the game:
{{description}}

These are some of the available character configurations for the game:
Classes: {{character_classes}}
Roles: {{character_types}}
Attributes: {{attributes}}

Where the rules are undefined, you must make them up. Make the game challenging and rewarding.

You may request that the players do activities, such as roll dice, in order to engage them in the story.

Tell a really good story.
{{/system~}}
{{#user~}}
Generate me a new character. The character has the class of {{character_class}} and the role of {{character_type}}.
{{/user~}}
{{#user~}}
First, what's the character's name?
{{/user~}}
{{#assistant~}}
{{gen 'name' max_tokens=20 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Now, assign attribute scores between 1 and 20 (inclusive) for all attributes: {{attributes}}

Respond as a comma delimited list with colons indicating the attributes score. 

This is the format: "Attribute Name: Score, Another Attribute Name: Score". 

For example:
Strength: 18, Dexterity: 12,

{{/user~}}
{{#assistant~}}
{{gen 'attributes' max_tokens=50 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Now, list the inventory as a comma delimited list.
{{/user~}}
{{#assistant~}}
{{gen 'inventory' max_tokens=100 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Now, give the user an exciting backstory. Make me want to play this character!
{{/user~}}
{{#assistant~}}
{{gen 'backstory' max_tokens=100 temperature=0.9}}
{{/assistant~}}
"""
)


def roll_character(campaign: Campaign) -> CreateCharacter:
    character_class = random.choice(campaign.character_classes)
    character_type = random.choice(campaign.character_types)
    program = gen_char(
        title=campaign.title,
        description=campaign.description,
        attributes=", ".join(default_attributes),
        character_classes=", ".join(campaign.character_classes),
        character_types=", ".join(campaign.character_types),
        character_class=character_class,
        character_type=character_type,
    )

    attributes = [xs.split(": ") for xs in program["attributes"].split(",")]
    attributes = {(k.strip()): int("".join(filter(str.isdigit, v))) for [k, v] in attributes}
    return CreateCharacter(
        name=program["name"],
        campaign_id=campaign.id,
        character_class=program["character_class"],
        character_type=program["character_type"],
        backstory=program["backstory"],
        attributes=attributes,
        primary_goal="",
        inventory=program["inventory"].split(", "),
    )


gen_campaign = guidance(
    '''
{{#system~}}
You are an author of RPG games
{{/system~}}
{{#user~}}
Create a game according to this premise:

"""
{{prompt}}
"""

First, Give the game a simple title
{{/user~}}
{{#assistant~}}
{{gen 'title' temperature=0.1 max_tokens=20}}
{{/assistant~}}
{{#user~}}
Now, introduce the game to potential players in a full paragraph. Tell us about the game world, story intrigue, and what makes this game unique.
{{/user~}}
{{#assistant~}}
{{gen 'description' temperature=0.9}}
{{/assistant~}}
{{#user~}}
That's great! Now lets describe a character class in the game. Respond with ONLY the character class name, prefixed with "Name:"

Example Response:
Name: Fighter

The first character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class1' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The second character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class2' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The third character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class3' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The fourth character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class4' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The fifth character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class5' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The sixth character class is:
{{/user~}}
{{#assistant~}}
{{gen 'class6' max_tokens=10 temperature=0.1}}
{{/assistant~}}

{{#user~}}
Now lets describe the socio-ethnic roles in the game. For example species, race, ethnic background, caste. Whatever fits the story. 

Respond with ONLY the character type name, prefixed with "Name:"

Example Response:
Name: Elf

The first character type is:
{{/user~}}
{{#assistant~}}
{{gen 'type1' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The second character type class is:
{{/user~}}
{{#assistant~}}
{{gen 'type2' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The third character type class is:
{{/user~}}
{{#assistant~}}
{{gen 'type3' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The fourth character type class is:
{{/user~}}
{{#assistant~}}
{{gen 'type4' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The fifth character type class is:
{{/user~}}
{{#assistant~}}
{{gen 'type5' max_tokens=10 temperature=0.1}}
{{/assistant~}}
{{#user~}}
The sixth character type class is:
{{/user~}}
{{#assistant~}}
{{gen 'type6' max_tokens=10 temperature=0.1}}
{{/assistant~}}

'''
)


def generate_campaign_raw(prompt: str) -> guidance.Program:
    return gen_campaign(prompt=prompt)


def generate_campaign(prompt: str) -> CreateCampaign:
    generated = generate_campaign_raw(prompt)
    return CreateCampaign(
        title=generated["title"].replace('"', ""),
        description=generated["description"].replace('"', ""),
        character_classes=[
            generated[f"class{i}"].replace("Name: ", "") for i in range(1, 7)
        ],
        character_types=[
            generated[f"type{i}"].replace("Name: ", "") for i in range(1, 7)
        ],
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
