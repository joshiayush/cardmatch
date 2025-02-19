from pydantic import BaseModel


class RevisedCreditCardRequest(BaseModel):
    unique_name: str


class QNARequest(BaseModel):
    cards_id: list[str]
    session_id: str
    question: str
