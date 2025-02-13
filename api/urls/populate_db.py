import os
from typing import Dict

import pandas as pd

from models.loaders.json_doc_loader import load_cc_json_doc_into_db


_cc_sheets = ["sbi", "axis", "hdfc"]


def load_cc_info() -> Dict:
    cc_info = dict()
    for sheet in _cc_sheets:
        df = pd.read_excel(os.getenv("CC_URLS_FILE_PATH"), sheet_name=sheet)
        cc_info.update(df.set_index("card_name").T.to_dict())
    return cc_info


def populate_db() -> Dict:
    cards = load_cc_info()
    docs = load_cc_json_doc_into_db(cards)
    return {"cards": docs}
