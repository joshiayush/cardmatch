from typing import Dict
from bson.objectid import ObjectId

from api.request_models.models import QNARequest
from api.db import credit_cards_collection
from models.seek_chain.qa_chain import configure_qa_chain


def qna(req: QNARequest) -> Dict:
    cc_docs = dict()
    for card_id in req.cards_id:
        doc = credit_cards_collection.find_one({"_id": ObjectId(card_id)})
        cc_docs[doc["card_name"]] = dict(card_link=doc["source"], tnc=doc["tnc"])

    qa_chain = configure_qa_chain(cc_docs, session_id=req.session_id)
    return dict(session_id=req.session_id, answer=qa_chain.run(req.question))
