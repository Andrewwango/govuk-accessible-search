import pydantic


class ChatGPTRequest(pydantic.BaseModel):
    query: str
    context: str
    history: list[dict] = []


class SelectRelevantSectionRequest(pydantic.BaseModel):
    query: str
    options: list[str]
    history: list[dict] = []


class TextToSpeechRequest(pydantic.BaseModel):
    text: str


class TextOutputResponse(pydantic.BaseModel):
    output: str
