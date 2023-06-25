from typing import AsyncIterator, List, TypeVar

import guidance
from pydantic import BaseModel

from rngesus.models import Chat

from ..database import Campaign, Character
from .. import config
from .prompts import throttle


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

Remember, as Dungeon master:
- If a scene requires resolution, use the character's attributes and die rolls to resolve it. Vary the size and quantity of the dice depending on the situation, and modify the results based on the size of the characters attributes. Include the math and the result of the roll in your response.
- NPCs have attributes too. Use their attributes in any equations, but don't reveal their rolls or attributes to the players.
- If a scenario comes up where the rules are not documented here, then make up a new rule. Make sure to explain the new rule to the players, and be consistent with any previous rules.
- Work with the characters, a game that grows organically with the player's curiosity and interests is more exciting. You can make new things up.
- Offer leading options or clues around what characters can do within a scene or scenario
- Do not speak, act, or narrate the feelings of the players characters. You run all of the non-player characters, but player characters listed above must instead be prompted for their actions
- The characters are acting as a collaborative team, but they may have their own interpersonal relationships. Encourage exploration of their dynamics. Make sure to be inclusive of all players
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


outakes = """
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
"""

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
    program = gen_chat(async_mode=True, stream=True, silent=config.SILENT_GUIDANCE, **kwargs)
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
