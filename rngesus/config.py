import os
from dotenv import load_dotenv
load_dotenv()
SILENT_GUIDANCE=os.environ.get("SILENT_GUIDANCE", False)
VERBOSE_DATABASE=os.environ.get("VERBOSE_DATABASE", True)
OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]
# OPENAI_MODEL=os.environ.get("OPENAI_MODEL", "gpt-4")
OPENAI_MODEL=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
