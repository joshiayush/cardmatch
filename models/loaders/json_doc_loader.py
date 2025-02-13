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
from langchain.llms.openai import OpenAI
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


def load_cc_json_doc(*, cc_name: str, cc_info: Dict) -> Dict:
    """Loads a credit card json doc from the url.

    Args:
        cc_info: The credit card source information.

    Returns:
        The credit card JSON document.
    """
    with open(_credit_cards_details_extractor_prompt, mode="r") as extractor:
        prompt = extractor.read()

    llm = OpenAI(model="gpt-4o")
    prompt_template = PromptTemplate.from_template(prompt)
    chain = prompt_template | llm | StrOutputParser()

    loader = WebBaseLoader(cc_info["card_link"])
    documents = loader.load()

    re = chain.invoke({"document": documents[0].page_content})
    json_doc = llm_response_to_json(re)["data"]
    json_doc["card_name"] = cc_name
    json_doc["card_link"] = documents[0].metadata["source"]
    json_doc["card_image"] = cc_info["card_image"]
    json_doc["tnc"] = cc_info["tnc"]
    json_doc["unique_name"] = get_credit_card_unique_name(
        documents[0].metadata["source"]
    )
    return json_doc


def load_cc_json_doc_into_db(cc_info: Dict, /, *, revised: bool = False) -> List[Dict]:
    """Loads a credit card JSON doc from each url."""
    json_docs = list()

    for key, info in cc_info.items():
        if info["card_link"] is np.nan:
            continue

        json_doc = load_cc_json_doc(cc_name=key, cc_info=info)
        credit_cards_collection.insert_one(json_doc)
        json_docs.append(json_doc)
    return json_docs
