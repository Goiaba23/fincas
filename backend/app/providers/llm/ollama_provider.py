import json
from typing import AsyncIterator

import httpx

from app.providers.llm import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3", embedding_model: str = "nomic-embed-text"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.embedding_model = embedding_model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = [
                {"type": "function", "function": {
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "parameters": t["function"].get("parameters", {}),
                }}
                for t in tools
            ]

        async with httpx.AsyncClient() as client:
            if stream:
                return self._stream(client, payload)

            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

            result = {"role": "assistant", "content": data.get("message", {}).get("content")}
            if data.get("message", {}).get("tool_calls"):
                result["tool_calls"] = [
                    {"id": tc.get("function", {}).get("name", ""),
                     "type": "function",
                     "function": {"name": tc.get("function", {}).get("name"),
                                  "arguments": json.dumps(tc.get("function", {}).get("arguments", {}))}}
                    for tc in data["message"]["tool_calls"]
                ]
            return result

    async def _stream(self, client: httpx.AsyncClient, payload: dict) -> AsyncIterator[str]:
        async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if chunk.get("done"):
                        break
                    if content := chunk.get("message", {}).get("content"):
                        yield content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient() as client:
            results = []
            for text in texts:
                resp = await client.post(f"{self.base_url}/api/embeddings", json={
                    "model": self.embedding_model,
                    "prompt": text,
                })
                resp.raise_for_status()
                results.append(resp.json()["embedding"])
            return results

    async def count_tokens(self, text: str) -> int:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/api/generate", json={
                "model": self.model,
                "prompt": text,
            })
            resp.raise_for_status()
            return resp.json().get("eval_count", 0)
