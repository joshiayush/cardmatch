import os
from typing import Dict

import pandas as pd

_cc_sheets = ["sbi", "axis", "hdfc"]


def load_cc_info() -> Dict:
    cc_info = dict()
    for sheet in _cc_sheets:
        df = pd.read_excel(os.getenv("CC_URLS_FILE_PATH"), sheet_name=sheet)
        cc_info.update(df.set_index("card_name").T.to_dict())
    return cc_info
