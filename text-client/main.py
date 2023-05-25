"""Simple text client for testing the backend."""

import requests
import typer

app = typer.Typer()


@app.command()
def main(backend_url: str = "https://shwast-fun-app.azurewebsites.net/api", action: str = "chatgpt"):
    context = typer.prompt("Context").strip()
    if not context:
        context = "This is test context. A freddo costs £2"

    while True:
        try:
            message = typer.prompt("Query").strip()
            if not message:
                continue

            response = requests.post(
                f"{backend_url}/{action}",
                json={
                    "context": context,
                    "query": message,
                },
            )
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
