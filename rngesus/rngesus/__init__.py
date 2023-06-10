from .campaign import *
from .character import *
from .chat import *
from .. import config

import guidance
import openai


openai.api_key = config.OPENAI_API_KEY
guidance.llm = guidance.llms.OpenAI(config.OPENAI_MODEL)
