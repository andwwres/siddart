"""Core agent — agentic loop with Claude + Meta Ads tools."""

from __future__ import annotations

import json
import os

import anthropic

from .meta_api import execute_tool
from .tools import TOOLS

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
MAX_TURNS = 20

SYSTEM_PROMPT = """\
Eres un experto en Meta Ads (Facebook/Instagram Ads). Ayudas a los usuarios a:
- Consultar cuentas, campañas, ad sets y sus métricas.
- Analizar rendimiento (spend, impressions, CTR, CPC, ROAS, purchases).
- Comparar cuentas y campañas con dashboards.
- Actualizar presupuestos (siempre confirmar antes con el usuario).

Reglas:
1. Siempre usa las herramientas disponibles para obtener datos reales — nunca inventes métricas.
2. Cuando el usuario pida datos, llama a la herramienta adecuada y presenta los resultados de forma clara.
3. Si el usuario quiere actualizar un presupuesto, SIEMPRE confirma el monto y la campaña antes de ejecutar update_campaign_budget.
4. Presenta dashboards y tablas en formato markdown cuando sea apropiado.
5. Si algo falla, explica el error y sugiere alternativas.
6. Los Account IDs funcionan con o sin prefijo act_.
7. Responde en el mismo idioma que el usuario.
"""


def run_agent(client: anthropic.Anthropic, messages: list[dict]) -> str:
    """Run the agentic loop until a final text response or max turns."""
    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Collect assistant content blocks
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # If stop reason is end_turn (no tool use), extract final text
        if response.stop_reason == "end_turn":
            text_parts = [block.text for block in assistant_content if block.type == "text"]
            return "\n".join(text_parts)

        # Process tool calls
        tool_results = []
        for block in assistant_content:
            if block.type != "tool_use":
                continue
            result = execute_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return "Se alcanzó el límite de turnos. Por favor intenta de nuevo con una pregunta más específica."
