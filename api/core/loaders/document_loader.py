import os
import pathlib
import json
import logging
from typing import List, Dict

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


from api.db import credit_cards_collection
from api.utils import get_credit_card_unique_name

load_dotenv()

BASE_PROMPTS_DIR = pathlib.Path(os.getenv("BASE_PROMPTS_DIR"))
_credit_cards_details_extractor_prompt = (
    BASE_PROMPTS_DIR / "extraction/credit_cards_details.txt"
)

JSON_SCHEMAS_DIR = pathlib.Path(os.getenv("JSON_SCHEMAS_DIR"))


def llm_response_to_json(message: str) -> Dict:
    """Structures the model response into JSON format.

    This function provides a unified value for all the responses obtained from the
    model.

    Args:
        message: The message string obtained from the JSON response.

    Returns:
        The JSON response.
    """
    data = {
        "type": None,
        "data": None,
    }

    try:
        # Attempt to parse the JSON response
        response = json.loads(message.replace("\n", ""))
        data["type"] = "json"
        data["data"] = response
    except json.JSONDecodeError:
        logging.warn("Parsing failed, attempting to extract JSON from a code block.")
        try:
            response = message.split("```json")[1].split("```")[0].strip()
            response = json.loads(response)
            data["type"] = "json"
            data["data"] = response
        except (IndexError, json.JSONDecodeError):
            logging.exception('Cannot parse JSON string "%s"' % message)

    if not data["data"]:
        data["type"] = "text"
        data["data"] = message

    return data


def load_docs_from_urls(cc_info: Dict, /, *, revised: bool = False) -> List[Dict]:
    """Loads a credit card JSON doc from each url."""
    json_docs = list()

    with open(_credit_cards_details_extractor_prompt, mode="r") as extractor:
        prompt = extractor.read()

        llm = ChatOpenAI(model="gpt-4o")
        prompt_template = PromptTemplate.from_template(prompt)
        chain = prompt_template | llm | StrOutputParser()

    for info in cc_info.values():
        if info["card_link"] is np.nan:
            continue

        scraped_data_loader = WebBaseLoader(info["card_link"])
        scraped_documents = scraped_data_loader.load()

        re = chain.invoke({"document": scraped_documents[0].page_content})

        json_doc = llm_response_to_json(re)["data"]
        json_doc["source"] = scraped_documents[0].metadata["source"]
        json_doc["card_image"] = info["card_image"]
        json_doc["tnc"] = info["tnc"]
        json_doc["unique_name"] = get_credit_card_unique_name(
            scraped_documents[0].metadata["source"]
        )
        if revised is False:
            credit_cards_collection.insert_one(json_doc)

        json_docs.append(json_doc)
    return json_docs


_cc_sheets = ["sbi", "axis", "hdfc"]


def load_cc_info() -> Dict:
    cc_info = dict()
    for sheet in _cc_sheets:
        df = pd.read_excel(os.getenv("CC_URLS_FILE_PATH"), sheet_name=sheet)
        cc_info.update(df.set_index("card_name").T.to_dict())
    return cc_info
