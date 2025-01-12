from typing import Dict

from fastapi import FastAPI

from api.urls.list_all_cards import list_all_cards
from api.urls.get_revised_credit_card import get_revised_credit_card
from api.request_models.models import RevisedCreditCardRequest

app = FastAPI()


@app.get("/api/list-all-cards", response_model=Dict[str, list])
async def list_all_cards_endpoint():
    return list_all_cards()


@app.post("/api/get-revised-credit-card", response_model=Dict)
async def get_revised_credit_card_endpoint(req: RevisedCreditCardRequest):
    return get_revised_credit_card(req)
