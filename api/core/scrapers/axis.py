from typing import List

import requests
from bs4 import BeautifulSoup

"""Collects all the credit card urls from Axis."""

_axis_credit_cards_url = "https://www.axisbank.com/retail/cards/credit-card"
_axis_base_url = "https://www.axisbank.com"

_axis_best_selling_credit_cards = [
    "https://www.axisbank.com/retail/cards/credit-card/axis-bank-ace-credit-card",
    "https://www.axisbank.com/retail/cards/credit-card/neo-credit-card",
    "https://www.axisbank.com/retail/cards/credit-card/my-zone-credit-card",
    "https://www.axisbank.com/retail/cards/credit-card/flipkart-axisbank-credit-card",
    "https://www.axisbank.com/retail/cards/credit-card/airtel-axis-bank-credit-card",
]


class Axis:
    """Loads urls of Axis credit cards of all categories."""

    def load_urls(self) -> List[str]:
        """Finds url of each credit card listed over the webpage."""
        urls = set()

        re = requests.get(_axis_credit_cards_url)
        soup = BeautifulSoup(re.content, "html.parser")
        card_items = soup.find_all("div", class_="card-item")
        for card_item in card_items:
            a = card_item.find("div", class_="btnSec").find("a", class_="btn1")
            if not a.get("href") in urls:
                urls.add(_axis_base_url + a.get("href"))
        return urls


def load_axis_credit_card_urls() -> List[str]:
    _axis_best_selling_credit_cards.extend(Axis().load_urls())
    return _axis_best_selling_credit_cards
