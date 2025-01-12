from typing import Dict

from bson.objectid import ObjectId

from api.request_models.models import RevisedCreditCardRequest
from api.db import credit_cards_collection
from api.core.loaders.document_loader import load_docs_from_urls


def get_revised_credit_card(req: RevisedCreditCardRequest) -> Dict:
    unique_name = req.unique_name
    doc = credit_cards_collection.find_one({"unique_name": unique_name})
    if doc is None:
        return {}

    docs = load_docs_from_urls([doc["source"]])
    _id = docs[0].pop("_id", None)
    credit_cards_collection.update_one({"_id": ObjectId(doc["_id"])}, {"$set": docs[0]})
    docs[0]["_id"] = str(_id)
    return docs[0]
