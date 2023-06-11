import random
import re

from typing import AsyncIterator, Dict, List

import guidance

from ..models import CharacterSummary

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
{{/system~}}
{{#user~}}
Generate me a new character. The character has the class of {{character_class}} and the role of {{character_type}}.
{{~#if characters}}
Make sure to make the character sufficiently unique. You've previously generated the following characters:
{{#each characters~}}
- name: {{this.name}} class: {{this.character_class}} type: {{this.character_type}}
{{~/each}}
{{/if~}}
{{/user~}}
{{#user~}}
First, what's the character's name? Respond concisely with just the name. For example: "Max Ernst"
{{/user~}}
{{#assistant~}}
{{gen 'name' max_tokens=20 temperature=0.1}}
{{/assistant~}}
{{#user~}}
Concisely in a single sentence, what's the characters primary story goal? 
{{/user~}}
{{#assistant~}}
{{gen 'primary_goal' max_tokens=100 temperature=0.9}}
{{~/assistant~}}
{{#user~}}
In 3 sentences: what's the character's backstory:
{{/user~}}
{{#assistant~}}
{{gen 'backstory' max_tokens=200 temperature=0.9}}
{{~/assistant~}}
{{#user~}}
Assign attribute scores between 1 and 19 (inclusive). Attribute scores should average around 11. Those useful for their class have higher scores. Use at least one odd and even number.
Available attributes: {{attributes}}.
Respond as a comma delimited list with colons indicating the attributes score. Use no other punctuation. This is the format: "Attribute Name: Number, Another Attribute Name: Number"
{{~/user~}}
{{#assistant~}}
{{gen 'attribute_results' max_tokens=50 temperature=0.1}}
{{/assistant~}}
{{#user~}}
List the inventory as a comma delimited list. Focus on the essentials that this character needs.
Respond with just the items separated by commas. For example: "Water pouch, Sword, Potion"
{{/user~}}
{{#assistant~}}
{{gen 'inventory' max_tokens=100 temperature=0.1}}
{{/assistant~}}
'''
)


async def roll_character(
    campaign: Campaign, 
    characters: List[CharacterSummary],
    update_frequency_seconds: int = 1
) -> AsyncIterator[Character]:
    character_class = random.choice(campaign.character_classes)
    character_type = random.choice(campaign.character_types)
    program = gen_char(
        description=campaign.summary,
        attributes=", ".join(campaign.attributes),
        characters=[x.dict() for x in characters[-5:]],
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
        name=re.sub("^Name: ", "", program.get("name") or "", re.RegexFlag.IGNORECASE),
        campaign_id=campaign_id,
        character_class=program.get("character_class") or "",
        character_type=program.get("character_type") or "",
        backstory=program.get("backstory") or "",
        attributes=attributes,
        primary_goal=program.get("primary_goal") or "",
        inventory=parse_comma_delimited_list(program.get("inventory") or ""),
    )
