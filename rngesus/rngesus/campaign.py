from typing import AsyncIterator, Dict

import guidance

from .. import config
from ..database import Campaign
from .prompts import parse_comma_delimited_list, throttle


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

- Get specific. How do players affect the game?
- Feel free to make up new rules that go beyond the standards of the genre.
- The game can only use standard tools available at a table-top: attributes, scores, dice, and a big imagination.
- You have as many dice as you want available to you: D4, D6, D8, D10, D12, D20, D100.
- For each mechanic, give an example. Include any calculations, such as dice roles, modifiers, etc.
{{/user~}}
{{#assistant~}}
{{~#if mechanics}}{{mechanics}}{{else}}{{gen 'mechanics' temperature=0.9}}{{/if}}
{{/assistant~}}
{{#user~}}
Write a reminder that can later be referred to in order to remember this game. No more than a paragraph, and focus on things that are unique to this game: title, setting, story, mechanics.
{{/user~}}
{{#assistant~}}
{{~#if summary}}{{summary}}{{else}}{{gen 'summary' temperature=0.3}}{{/if}}
{{/assistant~}}
'''
)


def generate_campaign_raw(**kwargs) -> AsyncIterator[Dict[str, any]]:
    return gen_campaign(async_mode=True, stream=True, silent=config.SILENT_GUIDANCE, **kwargs)


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
