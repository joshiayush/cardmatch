import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")

_card_match_db = os.environ.get("CARD_MATCH_DB")
_credit_cards_collection = os.environ.get("CREDIT_CARD_COLLECTION")

mongo_client = MongoClient(MONGO_URI)

card_match_db = mongo_client[_card_match_db]
credit_cards_collection = card_match_db[_credit_cards_collection]
