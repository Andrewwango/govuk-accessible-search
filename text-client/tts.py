"""Simple text client for testing backend TTS."""

import requests
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "https://shwast-fun-app.azurewebsites.net/api"):
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


if __name__ == "__main__":
    app()
