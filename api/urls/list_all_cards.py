from typing import Dict

from api.core.scrapers.sbi import load_sbi_credit_card_urls


def list_all_cards() -> Dict:
    cards = load_sbi_credit_card_urls()
    return {"cards": cards}
