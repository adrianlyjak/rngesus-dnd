import random
from typing import AsyncIterator, Dict

import guidance

from .prompts import parse_comma_delimited_list, parse_int_kv_dict, throttle

from ..database import Campaign, Character
from .. import config

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
        silent=config.SILENT_GUIDANCE,
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
