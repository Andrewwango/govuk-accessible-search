"""Simple text client for testing backend speech routes."""

import requests
import typer

app = typer.Typer()


def test_text_to_speech(backend_url: str):
    action = "text-to-speech"

    while True:
        try:
            text = typer.prompt("Text").strip()
            if not text:
                continue

            response = requests.post(f"{backend_url}/{action}", json={"text": text})
            response.raise_for_status()

            output = response.json()["output"]

            print(output)
            print()
        except typer.Abort:
            typer.echo("Exiting...")
            break
        except Exception as e:
            typer.echo(f"Error: {e}")


def test_speech_to_text(backend_url: str):
    action = "speech-to-text"

    while True:
        try:
            filepath = typer.prompt("Audio file").strip()
            if not filepath:
                continue

            with open(filepath, "rb") as audio_file:
                files = {"file": audio_file}
                response = requests.post(f"{backend_url}/{action}", files=files)

            response.raise_for_status()

            output = response.json()["output"]

            print(output)
            print()
        except typer.Abort:
            typer.echo("Exiting...")
            break
        except Exception as e:
            typer.echo(f"Error: {e}")


@app.command()
def main(backend_url: str = "https://shwast-fun-app.azurewebsites.net/api"):
    test_text_to_speech(backend_url)


if __name__ == "__main__":
    app()
