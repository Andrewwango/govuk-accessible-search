from typing import Annotated

import fastapi
import uvicorn

from accessible_search import preprocessing, prompts, protocol, services

app = fastapi.FastAPI()


@app.post("/api/chatgpt", response_model=protocol.TextOutputResponse)
def query_chatgpt(parameters: protocol.ChatGPTRequest):
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)

    prompt = prompts.construct_query_prompt(context, query)

    response_dict = services.perform_chat_completion(history, prompt, temperature=parameters.temperature)

    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/select-relevant-section")
def select_relevant_section(parameters: protocol.SelectRelevantSectionRequest):
    history = preprocessing.preprocess_history(parameters.history)
    query = preprocessing.preprocess_query(parameters.query)
    context = preprocessing.preprocess_context(parameters.context)

    prompt = prompts.construct_select_prompt(parameters.options, context, query)

    response_dict = services.perform_chat_completion(history, prompt, max_tokens=16)

    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/speech-to-text")
def speech_to_text(file: Annotated[bytes, fastapi.File()]):
    response_dict = services.perform_speech_to_text(content=file)
    return protocol.TextOutputResponse(**response_dict)


@app.post("/api/text-to-speech")
def text_to_speech(parameters: protocol.TextToSpeechRequest):
    response_dict = services.perform_text_to_speech(parameters.text)
    return protocol.TextOutputResponse(**response_dict)


if __name__ == "__main__":
    # For local testing only
    uvicorn.run("server:app", port=8000)
