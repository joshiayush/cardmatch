from pydantic import BaseModel


class RevisedCreditCardRequest(BaseModel):
    unique_name: str
