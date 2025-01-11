import re
from typing import List

import requests
from bs4 import BeautifulSoup

"""Collects all the credit card urls from Hdfc."""

_hdfc_credit_cards_url = "https://www.hdfcbank.com/personal/pay/cards/credit-cards"
_hdfc_base_url = "https://www.hdfcbank.com"


class Hdfc:
    """Loads urls of Hdfc credit cards of all categories."""

    def load_urls(self) -> List[str]:
        """Finds url of each credit card listed over the webpage."""
        urls = set()

        res = requests.get(_hdfc_credit_cards_url)
        soup = BeautifulSoup(res.content, "html.parser")
        pattern = re.compile(r"^/personal/pay/cards/credit-cards/")
        links = soup.find_all('a', href=pattern)
        for link in links:
            if not link.get("href") in urls:
                urls.add(_hdfc_base_url + link.get("href"))
        return urls


def load_hdfc_credit_card_urls() -> List[str]:
    return Hdfc().load_urls()
