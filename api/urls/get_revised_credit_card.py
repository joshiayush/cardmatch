from typing import Dict

from bson.objectid import ObjectId

from api.request_models.models import RevisedCreditCardRequest
from api.db import credit_cards_collection
from models.loaders.json_doc_loader import load_cc_json_doc


def get_revised_credit_card(req: RevisedCreditCardRequest) -> Dict:
    unique_name = req.unique_name
    doc = credit_cards_collection.find_one({"unique_name": unique_name})
    if doc is None:
        return {}

    doc = load_cc_json_doc(cc_name=doc["card_name"], cc_info=doc)
    _id = doc.pop("_id", None)
    credit_cards_collection.update_one({"_id": ObjectId(doc["_id"])}, {"$set": doc})
    doc["_id"] = str(_id)
    return doc
