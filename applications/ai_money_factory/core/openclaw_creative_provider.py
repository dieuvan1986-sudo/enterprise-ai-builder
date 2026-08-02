from __future__ import annotations

import json
import subprocess
from typing import Any


class OpenClawCreativeProvider:
    """
    AI provider backed by the existing OpenClaw Gateway.

    OpenClaw manages model credentials and routing.
    This adapter only requests creative generation and returns text.
    """

    def __init__(
        self,
        agent: str = "main",
        session_key: str = "agent:main:ai-money-factory-creative",
        thinking: str = "minimal",
        timeout: int = 180,
    ) -> None:
        self.agent = agent
        self.session_key = session_key
        self.thinking = thinking
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Creative prompt cannot be empty.")

        command = [
            "openclaw",
            "agent",
            "--agent",
            self.agent,
            "--session-key",
            self.session_key,
            "--message",
            prompt,
            "--thinking",
            self.thinking,
            "--timeout",
            str(self.timeout),
            "--json",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout + 30,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "OpenClaw creative generation timed out."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(
                f"OpenClaw creative generation failed: {error}"
            )

        return self._extract_text(result.stdout)

    @staticmethod
    def _extract_text(raw_output: str) -> str:
        try:
            payload: dict[str, Any] = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "OpenClaw returned invalid JSON."
            ) from exc

        if payload.get("status") != "ok":
            raise RuntimeError(
                "OpenClaw agent run did not complete successfully."
            )

        try:
            text = payload["result"]["payloads"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "OpenClaw response does not contain assistant text."
            ) from exc

        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(
                "OpenClaw returned an empty creative response."
            )

        return text.strip()
