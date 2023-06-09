import os
import random
import re
import time
from typing import AsyncIterator, Dict, List, TypeVar

import guidance
import openai
from pydantic import BaseModel

from rngesus.models import Chat

from .database import Campaign, Character

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# set the default language model used to execute guidance programs
guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")


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
Now, assign attribute scores between 1 and 20 (inclusive) for all attributes: {{attributes}}.
Remember to give characters high enough scores to have niches skills on the team, but low enough to leave room for growth.

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
        silent=False,
    )
    async for state in throttle(program, update_frequency_seconds):
        yield result_to_character(campaign.id, state)


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
{{~#if title}}{{title}}{{else}}{{gen 'title' temperature=1 max_tokens=20}}{{/if}}
{{~/assistant~}}
{{~#user~}}
Give us a quick elevator pitch!
{{~/user~}}
{{~#assistant~}}
{{~#if description}}{{description}}{{else}}{{gen 'description' temperature=1}}{{/if}}
{{~/assistant~}}
{{~#user~}}
Does the game have any character classes?
Respond with ONLY a comma delimited list of the the character class names. 
Respond with between 1 and 8 classes.
For example: "Attorney, Designer, Janitor"
{{~/user~}}
{{~#assistant~}}
{{~#if character_classes}}{{character_classes}}{{else}}{{gen 'character_classes' max_tokens=30 temperature=0.3}}{{/if}}
{{~/assistant~}}
{{#user~}}
Who are the types of people in this story and where do they come from? Describe the socio-ethnic types in the game. Whatever fits the story. 
Think outside of the box!
Respond with between 1 and 8 types.
Respond with ONLY a comma delimited list of the types. 
For example: "Human, Half-Alien, Sentient Printer"
{{/user~}}
{{#assistant~}}
{{~#if character_types}}{{character_types}}{{else}}{{gen 'character_types' max_tokens=30 temperature=0.3}}{{/if}}
{{/assistant~}}
{{#user~}}
What are the attributes in the game? Whatever fits the story.
Respond with only a comma delimited list of attribute names.
Respond with between 1 and 8 attributes.
For example: "Power, Influence, Magic, Luck, Flexibility"
{{/user~}}
{{#assistant~}}
{{~#if character_attributes}}{{character_attributes}}{{else}}{{gen 'character_attributes' max_tokens=30 temperature=0.3}}{{/if}}
{{/assistant~}}
{{#user~}}
What's the hook. Tell me about the game world, and the story intrigue.
Get specific. Tell me details about how the story starts: an intriguing scene or incident.
{{/user~}}
{{#assistant~}}
{{~#if story}}{{story}}{{else}}{{gen 'story' temperature=0.9}}{{/if}}
{{/assistant~}}
{{#user~}}
What are the mechanics? I want to know what makes this game unique from other RPGs! 

Get specific. How do players affect the game?
Feel free to make up new rules that go beyond the standards of the genre.
The game can only use standard tools available at a table-top: pencil, paper, dice, and a big imagination.
{{/user~}}
{{#assistant~}}
{{~#if mechanics}}{{mechanics}}{{else}}{{gen 'mechanics' temperature=0.9}}{{/if}}
{{/assistant~}}
{{#user~}}
Write a reminder that can later be referred to in order to remember this game. No more than a paragraph, and focus on things that are unique to this game: title, setting, story, mechanics.
{{/user~}}
{{#assistant~}}
{{~#if summary}}{{summary}}{{else}}{{gen 'summary' temperature=0.9}}{{/if}}
{{/assistant~}}
'''
)


def generate_campaign_raw(**kwargs) -> AsyncIterator[Dict[str, any]]:
    return gen_campaign(async_mode=True, stream=True, silent=False, **kwargs)


def generate_new_campaign(
    prompt: str,
    update_frequency_seconds: int = 5,
) -> AsyncIterator[Campaign]:
    return generate_campaign(Campaign(prompt=prompt), update_frequency_seconds)


async def generate_campaign(
    campaign: Campaign, update_frequency_seconds: int = 5
) -> AsyncIterator[Campaign]:
    description_parts = campaign.description.split("\n---\n")
    kwargs = {
        "prompt": campaign.prompt,
        "title": campaign.title,
        "description": "".join(description_parts[0:1]),
        "character_classes": ", ".join(campaign.character_classes),
        "character_types": ", ".join(campaign.character_types),
        "character_attributes": ", ".join(campaign.attributes),
        "story": "".join(description_parts[1:2]),
        "mechanics": "".join(description_parts[2:3]),
        "summary": campaign.summary,
    }
    async for generated in throttle(generate_campaign_raw(**kwargs)):
        merged = {k: v if v else generated.get(k) or "" for k, v in kwargs.items()}
        yield Campaign(
            id=campaign.id,
            prompt=campaign.prompt,
            title=(merged["title"]).replace('"', ""),
            description="\n---\n".join(
                [
                    merged["description"].replace('"', ""),
                    merged["story"],
                    merged["mechanics"],
                ]
            ),
            summary=(merged["summary"]),
            character_classes=parse_comma_delimited_list((merged["character_classes"])),
            character_types=parse_comma_delimited_list((merged["character_types"])),
            attributes=parse_comma_delimited_list((merged["character_attributes"])),
        )


def parse_comma_delimited_list(s: str) -> List[str]:
    return [re.sub("\.$", "", x.strip()) for x in s.split(",")]


gen_chat = guidance(
    """
{{#system~}}
# RPG Game

You are a dungeon master running a campaign for a table-top RPG game called "{{title}}" 

The following is a detailed description of the game and its rules:

'''
{{description}}
'''

## Campaign

You will come up with a unique campaign for the players. There are {{character_count}} players. They have chosen the following characters:

{{#each characters}}
---

## Character {{add 1 @index}}

- Name: {{this.name}}
- Class: {{this.character_class}}
- Type: {{this.character_type}}
- Attributes: {{this.attributes}}

### Backstory:

{{this.backstory}}

### Character Goal:

{{this.primary_goal}}
{{/each}}

# Prepare

Now, come up with a campaign

Start by making a short plan for the game

- Be concise
- This will not be told to the players, and is just your personal notes
- Keep the outline simple and structural
- Curate the story for the specific characters above
- Keep the story thread open, so that the story can organically evolve depending on the players actions

{{/system~}}
{{~#assistant~}}
{{~#if scenario}}{{gen 'scenario' temperature=1}}{{else}}{{scenario}}{{/if~}}
{{/assistant~}}
{{~#system~}}
Remember, as Dungeon master:
- If a scene requires resolution, use the character's attributes, and a little bit of randomness! If there's a random number or die roll required, roll a die and include the result in your response!
- If a scenario comes up where the rules are not documented here, then make up a new rule. Just explain the rule to the players, and be consistent with any previous rules.
- Work with the characters, a game that grows organically with the player's curiosity and interests is more exciting. You can make new things up.
- Be consistent

Now briefly introduce the story to the players. Set the scene, and ask what they'd like to do!

You start as dungeon master now:
{{~/system~}}
{{#each previous_messages~}}
{{#if (equal this.user_type "assistant")}}
{{#assistant~}}
{{this.message}}
{{/assistant~}}
{{/if~}}
{{#if (equal this.user_type "user")}}
{{#user~}}
{{this.message}}
{{/user~}}
{{/if~}}
{{/each~}}
{{#assistant~}}
{{gen 'next' temperature=1}}
{{/assistant}}
"""
)


class ChatResult(BaseModel):
    scenario: str
    assistant: str


async def generate_chat_unthrottled(
    campaign: Campaign, characters: List[Character], history: List[Chat]
) -> AsyncIterator[ChatResult]:
    # guidance.llms.OpenAI.cache.clear()
    kwargs = {
        "description": campaign.description,
        "summary": campaign.summary,
        "title": campaign.title,
        "scenario": campaign.scenario,
        "characters": [c.dict() for c in characters],
        "character_count": len(characters),
        "previous_messages": [x.dict() for x in history],
    }
    program = gen_chat(
        async_mode=True,
        stream=True,
        silent=True,
        **kwargs
    )
    # return ChatResult(scenario=generated["scenario"] or "", assistant=generated["next"] or "")
    async for generated in program:
        yield ChatResult(
            scenario=generated.get("scenario") or "",
            assistant=generated.get("next") or "",
        )


def generate_chat(
    campaign: Campaign, characters: List[Character], history: List[Chat]
) -> AsyncIterator[ChatResult]:
    return throttle(generate_chat_unthrottled(campaign, characters, history))


T = TypeVar("T")


async def throttle(
    iterator: AsyncIterator[T], update_frequency_seconds: int = 1
) -> AsyncIterator[T]:
    last = None
    result = None
    async for generated in iterator:
        result = generated
        now = time.time()
        if last is None or (now - last > update_frequency_seconds):
            last = now
            yield result
    if result:
        yield result
