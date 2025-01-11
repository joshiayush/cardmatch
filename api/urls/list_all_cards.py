from typing import Dict

from api.core.scrapers.sbi import load_sbi_credit_card_urls
from api.core.scrapers.axis import load_axis_credit_card_urls
from api.core.scrapers.hdfc import load_hdfc_credit_card_urls


def list_all_cards() -> Dict:
    cards = load_sbi_credit_card_urls()
    cards.extend(load_axis_credit_card_urls())
    cards.extend(load_hdfc_credit_card_urls())
    return {"cards": cards}
