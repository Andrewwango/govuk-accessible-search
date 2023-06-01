import os

from azure.cognitiveservices import speech
import openai

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_URL")
openai.api_version = "2023-05-15"

OPENAI_CHATGPT_DEPLOYMENT = os.getenv("OPENAI_CHATGPT_DEPLOYMENT")
OPENAI_GPT_DEPLOYMENT = os.getenv("OPENAI_GPT_DEPLOYMENT")

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
AZURE_SPEECH_VOICE = os.getenv("AZURE_SPEECH_VOICE")

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


def perform_speech_to_text(___) -> ...:
    speech_config = speech.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_recognition_language="en-US"
    # TODO: we probably want to use `stream=` not `filename=`
    audio_config = speech.audio.AudioConfig(filename=...)

    recognizer = speech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once_async().get()

    if result.reason == speech.ResultReason.NoMatch:
        raise ValueError("No valid speech detected")
    if result.reason == speech.ResultReason.Canceled:
        raise Exception("Error in speech recognition")

    return {
        "output": result.text
    }


def perform_text_to_speech(text: str) -> ...:
    speech_config = speech.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = AZURE_SPEECH_VOICE

    synthesizer = speech.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speech.ResultReason.Canceled:
        raise Exception("Error in speech synthesis")

    stream = speech.AudioDataStream(result)
    # TODO: maybe not just return the stream?
    return stream
