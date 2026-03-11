"""CLI entrypoint — interactive conversation with the Meta Ads agent."""

from __future__ import annotations

import os
import sys

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .agent import run_agent

console = Console()


def main() -> None:
    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY no está configurada. Copia .env.example a .env y complétala.")
        sys.exit(1)

    if not os.getenv("META_ACCESS_TOKEN"):
        console.print("[yellow]Advertencia:[/yellow] META_ACCESS_TOKEN no está configurada. Las llamadas a la API de Meta fallarán.")

    client = anthropic.Anthropic()
    messages: list[dict] = []

    console.print("\n[bold blue]Meta Ads Agent[/bold blue] — Escribe tu consulta o 'salir' para terminar.\n")

    while True:
        try:
            user_input = console.input("[bold green]Tú>[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Hasta luego.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            console.print("[dim]Hasta luego.[/dim]")
            break

        messages.append({"role": "user", "content": user_input})

        with console.status("[bold cyan]Pensando...[/bold cyan]"):
            response = run_agent(client, messages)

        console.print()
        console.print(Markdown(response))
        console.print()


if __name__ == "__main__":
    main()
