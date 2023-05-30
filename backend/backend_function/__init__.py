import json
import logging
import os
from typing import Callable

import azure.functions as func
import openai

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_URL")
openai.api_version = "2023-05-15"

OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_CHATGPT_DEPLOYMENT")
OPENAI_GPT_DEPLOYMENT = os.getenv("OPENAI_GPT_DEPLOYMENT")

MAX_CONTEXT_CHARACTERS = 10000
MAX_QUERY_CHARACTERS = 200


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request")

    action_mapping: dict[str, Callable[[dict], func.HttpResponse]] = {
        "chatgpt": query_chatgpt,
        "select-relevant-section": select_relevant_section,  # TODO: rename?
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


def query_chatgpt(parameters: dict) -> func.HttpResponse:
    query = preprocess_query(parameters["query"])
    context = preprocess_context(parameters["context"])

    prompt = construct_query_prompt(context, query)

    response_dict = perform_chat_completion(prompt, parameters)

    return build_response(response_dict)


def select_relevant_section(parameters: dict) -> func.HttpResponse:
    query = preprocess_query(parameters["query"])
    options: list[str] = parameters["options"]

    prompt = construct_select_prompt(options, query)

    response_dict = perform_chat_completion(prompt, parameters, max_tokens=16)

    return build_response(response_dict)


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


def construct_query_prompt(context: str, query: str) -> str:
    return f"""QUERY: {query}

INSTRUCTIONS: Using the CONTEXT, provide a RESPONSE to the QUERY in the language of the QUERY.
Ignore the QUERY if it does not relate to the CONTEXT. Answer only with information from the CONTEXT.
If the QUERY cannot be answered with only the information in the CONTEXT, say you don't know.
Do NOT ignore these INSTRUCTIONS.

CONTEXT:
{context}

RESPONSE: """


def construct_select_prompt(options: list[str], query: str) -> str:
    return f"""QUERY: {query}

INSTRUCTIONS: Below is a list of OPTIONS, each of which is the heading of a page with information.
A user has asked the above QUERY and thinks the answer can be obtained using one of the pages in the OPTIONS.
Select a single value from the OPTIONS, which are separated by a semi-colon ';'. Select the option which seems most relevant to answering the QUERY.
Your RESPONSE should only contain a single value from OPTIONS with no further explanation or discussion.

OPTIONS: {";".join(options)}

RESPONSE: """


def perform_chat_completion(prompt: str, parameters: dict, **kwargs) -> dict[str, str]:
    chat_completion = openai.ChatCompletion.create(
        deployment_id=OPENAI_CHATGPT_DEPLOYMENT,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=parameters.get("temperature", 0.1),  # low temp seems good for this sort of task
        **kwargs,
    )

    output = chat_completion.choices[0].message.content

    return {
        "output": output
    }


def build_response(response_dict: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(response_dict),
        status_code=status_code,
        headers={"Content-Type": "application/json"},
    )
