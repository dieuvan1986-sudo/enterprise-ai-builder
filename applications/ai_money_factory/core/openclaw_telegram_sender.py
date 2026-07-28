from __future__ import annotations

import os
import subprocess


class OpenClawTelegramSender:
    """
    Deliver messages through the existing OpenClaw Telegram channel.

    Telegram credentials remain managed by OpenClaw.
    The recipient target is supplied through an environment variable.
    """

    TARGET_ENV = "AI_MONEY_FACTORY_TELEGRAM_TARGET"

    def __init__(self, target: str | None = None) -> None:
        self.target = target or os.getenv(self.TARGET_ENV)

        if not self.target:
            raise ValueError(
                f"Telegram target is missing. "
                f"Set environment variable {self.TARGET_ENV}."
            )

    def send(self, message: str) -> None:
        if not message.strip():
            raise ValueError("Cannot send an empty Telegram message.")

        command = [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--target",
            self.target,
            "--message",
            message,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(
                f"OpenClaw Telegram delivery failed: {error}"
            )
