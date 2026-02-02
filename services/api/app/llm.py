from __future__ import annotations

import json
from typing import Any, AsyncGenerator

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You are a data analyst assistant that can call tools to answer questions.
Return a JSON object with either a tool call or a final answer.
""".strip()

DEVELOPER_PROMPT = """
Tool rules:
- Use run_sql for data questions. Only SELECT from table named dataset.
- Use summarize_dataframe when user asks for overall stats.
- Use plot to suggest a chart with x and y columns.
Output format:
{"type": "tool", "name": "run_sql", "arguments": {"query": "SELECT ..."}}
OR
{"type": "final", "message": "...", "table": {...}, "chart": {...}}
""".strip()

FEW_SHOTS = [
    {
        "role": "user",
        "content": "Show average value by category and chart it.",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "type": "tool",
                "name": "run_sql",
                "arguments": {
                    "query": "SELECT category, AVG(value) AS avg_value FROM dataset GROUP BY category",
                },
            }
        ),
    },
]


async def stream_ollama(messages: list[dict[str, str]], model: str, temperature: float) -> AsyncGenerator[str, None]:
    payload = {
        "model": model,
        "stream": True,
        "messages": messages,
        "options": {"temperature": temperature},
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
