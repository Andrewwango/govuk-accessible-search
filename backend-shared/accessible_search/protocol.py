import pydantic


class ChatGPTRequest(pydantic.BaseModel):
    query: str
    context: str
    history: list[dict] = []
    temperature: float = 0.0


class SelectRelevantSectionRequest(pydantic.BaseModel):
    query: str
    context: str = ""
    options: list[str]
    history: list[dict] = []


class TextToSpeechRequest(pydantic.BaseModel):
    text: str


class TextOutputResponse(pydantic.BaseModel):
    output: str
