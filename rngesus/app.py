from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from . import database

app = FastAPI()

from . import views
from . import api


@app.on_event("startup")
def on_startup():
    database.main()
