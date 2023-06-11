from typing import AsyncIterator, List, TypeVar

import guidance
from pydantic import BaseModel

from rngesus.models import Chat

from ..database import Campaign, Character
from .. import config
from .prompts import throttle


gen_loop = guidance(
  """
{{#system~}}
You are a dungeon master running a campaign for a table-top RPG game called "{{title}}"


{{/system~}}
  """
)