from typing import Dict

from fastapi import FastAPI

from api.urls.list_all_cards import list_all_cards

app = FastAPI()


@app.get("/list-all-cards", response_model=Dict[str, list])
async def list_all_cards_endpoint():
    return list_all_cards()
