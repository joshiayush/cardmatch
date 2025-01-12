import os
import pathlib
import json
import logging
from typing import List, Dict

from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from api.utils import get_credit_card_unique_name

load_dotenv()

BASE_PROMPTS_DIR = pathlib.Path(os.getenv("BASE_PROMPTS_DIR"))
_credit_cards_details_extractor_prompt = (
    BASE_PROMPTS_DIR / "extraction/credit_cards_details.txt"
)


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


def load_docs_from_urls(urls: List[str]) -> List[Dict]:
    """Loads a credit card JSON doc from each url."""
    loader = WebBaseLoader(urls)
    docs = loader.load()

    json_docs = list()
    with open(_credit_cards_details_extractor_prompt, mode="r") as extractor:
        prompt = extractor.read()

        llm = ChatOpenAI(model="gpt-4o")
        prompt_template = PromptTemplate.from_template(prompt)
        chain = prompt_template | llm | StrOutputParser()

        for doc in docs:
            re = chain.invoke({"document": doc.page_content})
            json_doc = llm_response_to_json(re)["data"]
            json_doc["source"] = doc.metadata["source"]
            json_doc["unique_name"] = get_credit_card_unique_name(
                doc.metadata["source"]
            )
            json_docs.append(json_doc)
    return json_docs
