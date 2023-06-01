import logging
import os

MAX_CONTEXT_CHARACTERS = int(os.getenv("MAX_CONTEXT_CHARACTERS", "10000"))
MAX_QUERY_CHARACTERS = int(os.getenv("MAX_QUERY_CHARACTERS", "200"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "4"))


def preprocess_history(history: list[dict]) -> list[dict]:
    if len(history) > MAX_HISTORY_MESSAGES:
        logging.warning("History too long, clipping...")
        history = history[-MAX_HISTORY_MESSAGES:]
    return history


def preprocess_query(query: str) -> str:
    if len(query) > MAX_QUERY_CHARACTERS:
        logging.warning("Query too long, truncating...")
        query = query[-MAX_QUERY_CHARACTERS:]
    return query


def preprocess_context(context: str) -> str:
    if len(context) > MAX_CONTEXT_CHARACTERS:
        logging.warning("Context too long, truncating...")
        context = context[-MAX_CONTEXT_CHARACTERS:]
    return context
