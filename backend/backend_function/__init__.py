import json
import logging
from typing import Callable

import azure.functions as func

from backend_function import preprocessing, prompts, services


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request")

    action_mapping: dict[str, Callable[[dict], func.HttpResponse]] = {
        "chatgpt": action_query_chatgpt,
        "select-relevant-section": action_select_relevant_section,
    }

    action = req.route_params.get("action")

    if action not in action_mapping:
        return func.HttpResponse(f"Invalid action: {action}", status_code=400)

    action_function = action_mapping[action]
    return action_function(req)


def action_query_chatgpt(request: func.HttpRequest) -> func.HttpResponse:
    try:
        parameters = request.get_json()
    except ValueError as e:
        return func.HttpResponse(f"Invalid parameters received: {e}", status_code=400)

    history = preprocessing.preprocess_history(parameters.get("history", []))
    query = preprocessing.preprocess_query(parameters["query"])
    context = preprocessing.preprocess_context(parameters["context"])

    prompt = prompts.construct_query_prompt(context, query)

    response_dict = services.perform_chat_completion(history, prompt, parameters)

    return build_json_response(response_dict)


def action_select_relevant_section(request: func.HttpRequest) -> func.HttpResponse:
    try:
        parameters = request.get_json()
    except ValueError as e:
        return func.HttpResponse(f"Invalid parameters received: {e}", status_code=400)

    history = preprocessing.preprocess_history(parameters.get("history", []))
    query = preprocessing.preprocess_query(parameters["query"])

    prompt = prompts.construct_select_prompt(parameters["options"], query)

    response_dict = services.perform_chat_completion(history, prompt, parameters, max_tokens=16)

    return build_json_response(response_dict)


def action_speech_to_text(request: func.HttpRequest) -> func.HttpResponse:
    # TODO: do some validation on this file
    file = request.files.values()[0]
    contents = file.stream.read()

    response_dict = services.perform_speech_to_text(contents)

    return build_json_response(response_dict)


def action_text_to_speech(request: func.HttpRequest) -> func.HttpResponse:
    try:
        parameters = request.get_json()
    except ValueError as e:
        return func.HttpResponse(f"Invalid parameters received: {e}", status_code=400)

    # TODO


def build_json_response(response_dict: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(response_dict),
        status_code=status_code,
        headers={"Content-Type": "application/json"},
    )
