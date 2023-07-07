"""Request handlers."""

import json
from typing import AsyncIterable

from accessible_search import preprocessing, prompts, protocol, services


def _prepare_query(parameters: protocol.ChatGPTRequest) -> tuple[list[dict], str, float]:
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)
    prompt = prompts.construct_query_prompt(context, query)
    return history, prompt, parameters.temperature


def handle_query_chatgpt(parameters: protocol.ChatGPTRequest) -> protocol.TextOutputResponse:
    history, prompt, temperature = _prepare_query(parameters)
    return services.perform_chat_completion(history, prompt, temperature=temperature)


async def handle_query_chatgpt_async(parameters: protocol.ChatGPTRequest) -> protocol.TextOutputResponse:
    history, prompt, temperature = _prepare_query(parameters)
    return await services.perform_chat_completion_async(history, prompt, temperature=temperature)


async def handle_query_chatgpt_stream(parameters: protocol.ChatGPTRequest) -> AsyncIterable[str]:
    history, prompt, temperature = _prepare_query(parameters)
    async for result in services.perform_chat_completion_streaming(history, prompt, temperature=temperature):
        yield json.dumps({"data": result}) + "\n"


def _prepare_select(parameters: protocol.SelectRelevantSectionRequest) -> tuple[list[dict], str]:
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)
    prompt = prompts.construct_select_prompt(parameters.options, context, query)
    return history, prompt


def handle_select_relevant_section(parameters: protocol.SelectRelevantSectionRequest) -> protocol.TextOutputResponse:
    history, prompt = _prepare_select(parameters)
    return services.perform_chat_completion(history, prompt, max_tokens=16)


async def handle_select_relevant_section_async(parameters: protocol.SelectRelevantSectionRequest) -> protocol.TextOutputResponse:
    history, prompt = _prepare_select(parameters)
    return await services.perform_chat_completion_async(history, prompt, max_tokens=16)
