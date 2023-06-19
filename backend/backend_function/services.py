import base64
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


def perform_speech_to_text(filename: str) -> dict:
    speech_config = speech.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US"
    audio_config = speech.audio.AudioConfig(filename=filename)

    recognizer = speech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once_async().get()

    if result.reason == speech.ResultReason.NoMatch:
        return {
            "output": ""
        }
    if result.reason == speech.ResultReason.Canceled:
        error_message = "Error in speech transcription"
        cancellation_details = result.cancellation_details
        if cancellation_details.reason == speech.CancellationReason.Error:
            error_message = "Error details: {}".format(cancellation_details.error_details)
        raise Exception(error_message)

    return {
        "output": result.text
    }


def perform_text_to_speech(text: str) -> dict:
    speech_config = speech.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    synthesizer = speech.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speech.ResultReason.Canceled:
        error_message = "Error in speech synthesis"
        cancellation_details = result.cancellation_details
        if cancellation_details.reason == speech.CancellationReason.Error:
            if cancellation_details.error_details:
                error_message = "Error details: {}".format(cancellation_details.error_details)
        raise Exception(error_message)

    audio_data = bytearray()
    buffer = bytes(16000)
    stream = speech.AudioDataStream(result)

    while (filled_size := stream.read_data(buffer)) > 0:
        audio_data.extend(buffer[:filled_size])

    return {
        "output": base64.b64encode(audio_data).decode()
    }
