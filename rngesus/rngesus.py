import os
import random
import re
import time
from typing import AsyncIterator, Dict, List

import guidance
import openai

from .database import Campaign, Character

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
{{gen 'attribute_results' max_tokens=50 temperature=0.1}}
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


async def roll_character(
    campaign: Campaign, update_frequency_seconds: int = 1
) -> AsyncIterator[Character]:
    character_class = random.choice(campaign.character_classes)
    character_type = random.choice(campaign.character_types)
    program = gen_char(
        description=campaign.summary,
        attributes=", ".join(campaign.attributes),
        character_class=character_class,
        character_type=character_type,
        async_mode=True,
        stream=True,
        silent=True,
    )
    result = None
    last = None
    async for state in program:
        result = result_to_character(campaign.id, state)
        now = time.time()
        if last is None or now - last > update_frequency_seconds:
            last = now
            yield result
    yield result


def result_to_character(campaign_id: int, program: Dict[str, any]) -> Character:
    attributes = parse_int_kv_dict(program.get("attribute_results") or "")
    return Character(
        name=program.get("name") or "",
        campaign_id=campaign_id,
        character_class=program.get("character_class") or "",
        character_type=program.get("character_type") or "",
        backstory=program.get("backstory") or "",
        attributes=attributes,
        primary_goal=program.get("primary_goal") or "",
        inventory=parse_comma_delimited_list(program.get("inventory") or ""),
    )


def parse_int_kv_dict(kv_list: str) -> Dict[str, int]:
    as_list = parse_comma_delimited_list(kv_list)
    split_list = [[y.strip() for y in x.split(":")] for x in as_list]
    cleaned_split = {
        x[0]: int(x[1]) for x in split_list if len(x) == 2 and re.match(r"^\d+$", x[1])
    }
    return cleaned_split


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
Write a reminder that can later be referred to in order to remember this game.
Write a paragraph of the things that are uniqe to this game, (title, setting, story, mechanics)
{{/user~}}
{{#assistant~}}
{{gen 'summary' temperature=0.9}}
{{/assistant~}}
'''
)


def generate_campaign_raw(prompt: str) -> AsyncIterator[Dict[str, any]]:
    return gen_campaign(
        prompt=prompt,
        class_count=2,
        type_count=2,
        attribute_count=2,
        async_mode=True,
        stream=True,
        silent=True,
    )


async def generate_campaign(
    prompt: str, update_frequency_seconds: int = 5
) -> AsyncIterator[Campaign]:
    generator = generate_campaign_raw(prompt)
    last = None
    result = None
    async for generated in generator:
        result = result_to_campaign(generated)
        now = time.time()
        if last is None or (now - last > update_frequency_seconds):
            last = now
            yield result
    yield result


def result_to_campaign(generated: Dict[str, any]) -> Campaign:
    return Campaign(
        title=(generated.get("title") or "").replace('"', ""),
        description=(generated.get("description") or "").replace('"', "")
        + "\n"
        + (generated.get("story") or "")
        + "\n"
        + (generated.get("mechanics") or "")
        + "\n"
        + "\n".join(generated.get("mechanics_continued") or []),
        summary=(generated.get("summary") or ""),
        character_classes=parse_comma_delimited_list(
            (generated.get("character_classes") or "")
        ),
        character_types=parse_comma_delimited_list(
            (generated.get("character_types") or "")
        ),
        attributes=parse_comma_delimited_list(
            (generated.get("character_attributes") or "")
        ),
    )


def parse_comma_delimited_list(s: str) -> List[str]:
    return [re.sub("\.$", "", x.strip()) for x in s.split(",")]
