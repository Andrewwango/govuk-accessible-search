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


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request")

    action_mapping: dict[str, Callable] = {
        "chatgpt": query_chatgpt
    }

    action = req.route_params.get("action")

    if action not in action_mapping:
        return func.HttpResponse(f"Invalid action: {action}", status_code=400)

    try:
        request_json: dict = req.get_json()
    except ValueError as e:
        return func.HttpResponse(f"Invalid parameters received: {e}", status_code=400)

    return action_mapping[action](request_json)


def query_chatgpt(parameters: dict) -> func.HttpResponse:
    # TODO: support history?
    prompt = parameters["input"]

    # TODO: this is very approximate
    if len(prompt) > 5000:
        logging.warning("Prompt too long, truncating")
        prompt = prompt[-5000:]

    chat_completion = openai.ChatCompletion.create(
        deployment_id=OPENAI_CHATGPT_DEPLOYMENT,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    output = chat_completion.choices[0].message.content

    response = {
        "output": output
    }

    return func.HttpResponse(
        response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )


def query_gpt(parameters: dict) -> func.HttpResponse:
    prompt = parameters["input"]

    # TODO: this is very approximate
    if len(prompt) > 5000:
        logging.warning("Prompt too long, truncating")
        prompt = prompt[-5000:]

    completion = openai.Completion.create(
        prompt=prompt,
        deployment_id=OPENAI_GPT_DEPLOYMENT,
        model="text-davinci-003",
        temperature=parameters.get("temperature", 0.1),  # low temp seems good for this sort of task
    )

    output = completion["choices"][0]["text"].strip()

    response = {
        "output": output
    }

    return func.HttpResponse(
        response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
