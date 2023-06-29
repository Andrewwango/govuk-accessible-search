import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated

import fastapi
import uvicorn

from accessible_search import preprocessing, prompts, protocol, services

app = fastapi.FastAPI()

rate_limit_lock = asyncio.Lock()
rate_limit_data = defaultdict(list)
rate_limit_times = 10
rate_limit_window = timedelta(seconds=60)


@app.middleware("http")
async def rate_limit_middleware(request: fastapi.Request, call_next):
    """Rudimentary in-memory rate limiting solution."""
    global rate_limit_data

    client_ip = request.client.host
    current_time = datetime.now()

    async with rate_limit_lock:
        rate_limit_data[client_ip] = [
            time for time in rate_limit_data[client_ip]
            if current_time - time < rate_limit_window
        ]

        if len(rate_limit_data[client_ip]) >= rate_limit_times:
            raise fastapi.HTTPException(status_code=429, detail="Too Many Requests")

        rate_limit_data[client_ip].append(current_time)

    return await call_next(request)


@app.post("/api/chatgpt", response_model=protocol.TextOutputResponse)
async def query_chatgpt(parameters: protocol.ChatGPTRequest):
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)

    prompt = prompts.construct_query_prompt(context, query)

    response_dict = await services.perform_chat_completion_async(history, prompt, temperature=parameters.temperature)

    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/select-relevant-section")
async def select_relevant_section(parameters: protocol.SelectRelevantSectionRequest):
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)

    prompt = prompts.construct_select_prompt(parameters.options, context, query)

    response_dict = await services.perform_chat_completion_async(history, prompt, max_tokens=16)

    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/speech-to-text")
async def speech_to_text(file: Annotated[bytes, fastapi.File()]):
    response_dict = services.perform_speech_to_text(content=file)
    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/text-to-speech")
async def text_to_speech(parameters: protocol.TextToSpeechRequest):
    response_dict = services.perform_text_to_speech(parameters.text)
    return protocol.TextOutputResponse(**response_dict)


if __name__ == "__main__":
    # For local testing only
    uvicorn.run("server:app", port=8000)
