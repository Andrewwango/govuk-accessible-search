"""Simple text client for testing the backend."""

import requests
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "https://shwast-fun-app.azurewebsites.net/api"):
    action = typer.prompt("Action [chatgpt, select-relevant-section]")
    context = typer.prompt("Context").strip() if action == "chatgpt" else None
    options = typer.prompt("Options").strip() if action == "select-relevant-section" else None

    if not context:
        context = "This is test context. A freddo costs £2"

    while True:
        try:
            message = typer.prompt("Query").strip()
            if not message:
                continue

            request_dict = {
                "query": message,
            }

            if action == "chatgpt":
                request_dict["context"] = context
            elif action == "select-relevant-section":
                request_dict["options"] = options.split(",")

            response = requests.post(f"{backend_url}/{action}", json=request_dict)
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
