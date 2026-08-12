import json

import httpx
from django.conf import settings


class OllamaError(Exception):
    pass


class OllamaClient:
    def __init__(self, host: str | None = None, timeout: float = 120.0):
        self.host = host or settings.OLLAMA_HOST
        self.timeout = timeout

    def generate_json(self, model: str, prompt: str) -> dict:
        """Call Ollama's /api/generate with format=json and return the parsed dict.

        Raises OllamaError on transport failure or if the response body isn't valid JSON.
        Schema validity is the caller's responsibility.
        """
        try:
            resp = httpx.post(
                f"{self.host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama request failed: {exc}") from exc

        body = resp.json()
        raw = body.get("response", "")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError(f"Ollama returned non-JSON response: {raw[:200]!r}") from exc

    def embed(self, model: str, text: str) -> list[float]:
        try:
            resp = httpx.post(
                f"{self.host}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaError(f"Ollama embedding request failed: {exc}") from exc

        return resp.json()["embedding"]
