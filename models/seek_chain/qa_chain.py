import os
import pathlib
from typing import Any, Dict, Optional

import numpy as np
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.schema import BaseRetriever, Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")


class DocumentLoaderException(Exception):
    pass


class EPubReader(UnstructuredEPubLoader):
    def __init__(self, file_path: str | list[str], **kwargs: Any):
        super().__init__(file_path, **kwargs, mode="elements", strategy="fast")


class DocumentLoader(object):
    """Loads in a document with a supported extension."""

    supported_extensions = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".epub": EPubReader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader,
    }


def load_document(filepath: str) -> list[Document]:
    """Load a file and return it as a list of Document."""
    ext = pathlib.Path(filepath).suffix

    loader = DocumentLoader.supported_extensions.get(ext)
    if not loader:
        raise DocumentLoaderException(f"Unsupported file extension: {ext}")

    return loader(filepath).load()


def configure_retriever(
    docs: list[Document], use_compression: Optional[bool] = False
) -> BaseRetriever:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=200, separators=["\n\n## ", "\n\n", "\n", ". "]
    )
    splits = text_splitter.split_documents(docs)

    for i, split in enumerate(splits):
        split.metadata["section_id"] = i // 10

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(splits, embeddings)

    base_retriever = vectordb.as_retriever(
        search_type="mmr", search_kwargs={"k": 6, "fetch_k": 20, "alpha": 0.6}
    )
    retriever = MultiQueryRetriever.from_llm(
        llm=ChatOpenAI(temperature=0), retriever=base_retriever
    )
    if use_compression:
        embeddings_filter = EmbeddingsFilter(
            embeddings=embeddings, similarity_threshold=0.76
        )
        return ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=retriever
        )
    return retriever


DB_NAME = "chatbot_db"
COLLECTION_NAME = "chat_history"

custom_prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template="""You are a helpful AI assistant.

Given the following:
- **Chat History:**
  {chat_history}
- **Retrieved Context:**
  {context}
- **User's Latest Question:**
  {question}

Generate a response that maintains conversation context and utilizes relevant retrieved
information.
""",
)


def configure_chain(retriever: BaseRetriever, *, session_id: str) -> Chain:
    """Configure chain with a retriever."""
    chat_memory = MongoDBChatMessageHistory(
        connection_string=MONGO_URI,
        database_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        session_id=session_id,
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history", chat_memory=chat_memory, return_messages=True
    )
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    return ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
        verbose=True,
    )


def configure_qa_chain(cc_info: Dict, *, session_id: str) -> Chain:
    """Read documents, configure retriever, and the chain."""
    docs = []
    for _, info in cc_info.items():

        if info["card_link"] is np.nan and info["tnc"] is np.nan:
            raise ValueError('Either "card_link" or "tnc" needed.')

        if not info["card_link"] is np.nan:
            card_doc = WebBaseLoader(info["card_link"]).load()
            docs.extend(card_doc)

        if not info["tnc"] is np.nan:
            tnc_doc = load_document(info["tnc"])
            docs.extend(tnc_doc)

    retriever = configure_retriever(docs, use_compression=True)
    return configure_chain(retriever, session_id=session_id)
