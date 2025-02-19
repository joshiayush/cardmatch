from typing import Dict

from models.loaders.json_doc_loader import load_cc_json_doc_into_db
from api.cc_loader import load_cc_info


def populate_db() -> Dict:
    cards = load_cc_info()
    docs = load_cc_json_doc_into_db(cards)
    return {"cards": docs}
