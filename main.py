from typing import Dict

from fastapi import FastAPI

from api.urls.populate_db import populate_db
from api.urls.get_revised_credit_card import get_revised_credit_card
from api.request_models.models import RevisedCreditCardRequest

app = FastAPI()


@app.get("/api/populate-db", response_model=Dict[str, list])
async def populate_db_endpoint():
    return populate_db()


@app.post("/api/get-revised-credit-card", response_model=Dict)
async def get_revised_credit_card_endpoint(req: RevisedCreditCardRequest):
    return get_revised_credit_card(req)
