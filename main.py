from typing import Dict

from fastapi import FastAPI

from api.urls.populate_db import populate_db
from api.urls.get_revised_credit_card import get_revised_credit_card
from api.urls.get_credit_cards_list import get_credit_cards_list
from api.urls.qna import qna
from api.request_models.models import (
    RevisedCreditCardRequest,
    QNARequest,
)

app = FastAPI()


@app.get("/api/populate-db", response_model=Dict[str, list])
async def populate_db_endpoint():
    return populate_db()


@app.post("/api/get-revised-credit-card", response_model=Dict)
async def get_revised_credit_card_endpoint(req: RevisedCreditCardRequest):
    return get_revised_credit_card(req)


@app.get("/api/cards/list", response_model=Dict)
async def get_credit_cards_list_endpoint():
    return get_credit_cards_list()


@app.post("/api/cards/qna", response_model=Dict)
async def qna_endpoint(req: QNARequest):
    return qna(req)
