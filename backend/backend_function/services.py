import os

import openai

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_URL")
openai.api_version = "2023-05-15"

OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_CHATGPT_DEPLOYMENT")
OPENAI_GPT_DEPLOYMENT = os.getenv("OPENAI_GPT_DEPLOYMENT")

LLM_DEFAULT_TEMPERATURE = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.1"))


def perform_chat_completion(history: list[dict], prompt: str, parameters: dict, **kwargs) -> dict[str, str]:
    messages = history + [{"role": "user", "content": prompt}]

    chat_completion = openai.ChatCompletion.create(
        deployment_id=OPENAI_CHATGPT_DEPLOYMENT,
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=parameters.get("temperature", LLM_DEFAULT_TEMPERATURE),
        **kwargs,
    )

    output = chat_completion.choices[0].message.content

    return {
        "output": output
    }
