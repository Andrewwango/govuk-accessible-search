import json
import logging
import os
from typing import Callable

import azure.functions as func
import openai

from backend_function import prompts

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_URL")
openai.api_version = "2023-05-15"

OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_CHATGPT_DEPLOYMENT")
OPENAI_GPT_DEPLOYMENT = os.getenv("OPENAI_GPT_DEPLOYMENT")

MAX_CONTEXT_CHARACTERS = int(os.getenv("MAX_CONTEXT_CHARACTERS", "10000"))
MAX_QUERY_CHARACTERS = int(os.getenv("MAX_QUERY_CHARACTERS", "200"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "4"))


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request")

    action_mapping: dict[str, Callable[[dict], func.HttpResponse]] = {
        "chatgpt": action_query_chatgpt,
        "select-relevant-section": action_select_relevant_section,
    }

    action = req.route_params.get("action")

    if action not in action_mapping:
        return func.HttpResponse(f"Invalid action: {action}", status_code=400)

    try:
        request_json: dict = req.get_json()
    except ValueError as e:
        return func.HttpResponse(f"Invalid parameters received: {e}", status_code=400)

    action_function = action_mapping[action]
    return action_function(request_json)


def action_query_chatgpt(parameters: dict) -> func.HttpResponse:
    history = preprocess_history(parameters.get("history", None))
    query = preprocess_query(parameters["query"])
    context = preprocess_context(parameters["context"])

    prompt = prompts.construct_query_prompt(context, query)

    response_dict = perform_chat_completion(history, prompt, parameters)

    return build_json_response(response_dict)


def action_select_relevant_section(parameters: dict) -> func.HttpResponse:
    history = preprocess_history(parameters.get("history", None))
    query = preprocess_query(parameters["query"])

    prompt = prompts.construct_select_prompt(parameters["options"], query)

    response_dict = perform_chat_completion(history, prompt, parameters, max_tokens=16)

    return build_json_response(response_dict)


def preprocess_history(history: list[dict]) -> list[dict]:
    if history is None:
        return []
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


def perform_chat_completion(history: list[dict], prompt: str, parameters: dict, **kwargs) -> dict[str, str]:
    messages = history + [{"role": "user", "content": prompt}]

    chat_completion = openai.ChatCompletion.create(
        deployment_id=OPENAI_CHATGPT_DEPLOYMENT,
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=parameters.get("temperature", 0.1),  # low temp seems good for this sort of task
        **kwargs,
    )

    output = chat_completion.choices[0].message.content

    return {
        "output": output
    }


def build_json_response(response_dict: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(response_dict),
        status_code=status_code,
        headers={"Content-Type": "application/json"},
    )
