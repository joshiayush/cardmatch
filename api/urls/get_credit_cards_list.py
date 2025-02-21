from typing import Dict

from api.db import credit_cards_collection


def get_credit_cards_list() -> Dict:
    def serialize_document(doc):
        """Convert MongoDB ObjectId to a string in each document."""
        doc["_id"] = str(doc["_id"])
        return doc

    cards = [serialize_document(doc) for doc in credit_cards_collection.find()]
    return dict(cards=cards)
