from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from . import database


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

from . import views
from . import api


@app.on_event("startup")
def on_startup():
    database.main()
