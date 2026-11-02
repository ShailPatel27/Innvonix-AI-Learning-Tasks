import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

MODULE_DIR = Path(__file__).resolve().parent
load_dotenv(MODULE_DIR / ".env")


def get_chat_model():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Set GOOGLE_API_KEY in M9_LangGraph/.env.")
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
    )


def get_embeddings():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Set GOOGLE_API_KEY in M9_LangGraph/.env.")
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-2"),
        dimensions=32,
    )
