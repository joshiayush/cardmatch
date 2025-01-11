from typing import Dict, List

from api.core.scrapers.sbi import load_sbi_credit_card_urls
from api.core.scrapers.axis import load_axis_credit_card_urls
from api.core.scrapers.hdfc import load_hdfc_credit_card_urls
from api.core.loaders.document_loader import load_docs_from_urls


def _sanitize_https_urls(urls: List[str]) -> List[str]:
    """Filters a list of URLs and returns only those that start with 'https://'.

    Args:
        urls (List[str]): A list of URLs.

    Returns:
        List[str]: A list of URLs that start with 'https://'.
    """
    return [url for url in urls if url.startswith("https://")]


def list_all_cards() -> Dict:
    cards = load_sbi_credit_card_urls()
    cards.extend(load_axis_credit_card_urls())
    cards.extend(load_hdfc_credit_card_urls())

    cards = _sanitize_https_urls(cards)
    docs = load_docs_from_urls(cards)
    return {"cards": docs}
