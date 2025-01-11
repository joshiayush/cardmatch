from typing import List

import requests
from bs4 import BeautifulSoup

"""Collects all the credit card urls from SBI."""

_category_lifestyle = "https://www.sbicard.com/en/personal/credit-cards.page#lifestyle"
_category_rewards = "https://www.sbicard.com/en/personal/credit-cards.page#reward"
_category_shopping = "https://www.sbicard.com/en/personal/credit-cards.page#shopping"
_category_travel_and_fuel = (
    "https://www.sbicard.com/en/personal/credit-cards.page#travel---fuel"
)
_category_banking_partnership = (
    "https://www.sbicard.com/en/personal/credit-cards.page#banking-partnership"
)
_category_business = "https://www.sbicard.com/en/personal/credit-cards.page#business"


_learn_more_link_cls = "learn-more-link"


class Sbi:
    """Loads urls of Sbi credit cards of all categories."""

    def __init__(self, categories: List[str]) -> None:
        self._categories = categories

    def load_urls(self) -> List[str]:
        """Finds url of each credit card listed over the webpage."""
        urls = set()
        for category in self._categories:
            re = requests.get(category)

            soup = BeautifulSoup(re.content, "html.parser")
            links = soup.find_all("a", class_=_learn_more_link_cls)
            for link in links:
                if not link.get("href") in urls:
                    urls.add(link.get("href"))
        return list(urls)


def load_sbi_credit_card_urls() -> List[str]:
    return Sbi(
        [
            _category_lifestyle,
            _category_rewards,
            _category_shopping,
            _category_travel_and_fuel,
            _category_banking_partnership,
            _category_business,
        ]
    ).load_urls()
