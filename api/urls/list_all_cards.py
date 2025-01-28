from typing import Dict, List

from api.core.loaders.document_loader import load_docs_from_urls
from api.core.loaders.document_loader import load_cc_info


def list_all_cards() -> Dict:
    cards = load_cc_info()
    docs = load_docs_from_urls(cards)
    return {"cards": docs}
