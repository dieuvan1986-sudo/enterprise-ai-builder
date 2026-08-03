from __future__ import annotations

import logging
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from applications.ai_money_factory.core.video_factory import (
    VideoPackage,
    VideoScene,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VoiceSceneRender:
    scene_number: int
    purpose: str
    narration: str
    audio_path: Path


@dataclass(slots=True)
class VoiceRenderResult:
    title: str
    output_dir: Path
    scenes: list[VoiceSceneRender]


class VoiceRenderError(RuntimeError):
    """
    Raised when OpenClaw TTS cannot produce the requested voice asset.
    """


class OpenClawVoiceRenderer:
    """
    Render a VideoPackage narration track using the OpenClaw CLI.

    OpenClaw owns provider credentials and model routing. This adapter only
    passes scene narration to the existing TTS command and verifies WAV files.
    """

    def __init__(
        self,
        output_dir: str | Path,
        *,
        timeout: int = 120,
        max_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if timeout < 1:
            raise ValueError("timeout must be at least 1 second.")

        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds

    def render(self, package: VideoPackage) -> VoiceRenderResult:
        if not package.scenes:
            raise ValueError("VideoPackage must contain at least one scene.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "Rendering voice package '%s' with %s scenes into %s.",
            package.title,
            len(package.scenes),
            self.output_dir,
        )

        rendered_scenes: list[VoiceSceneRender] = []

        for scene in package.scenes:
            audio_path = self._audio_path_for(scene)
            self._render_scene(scene, audio_path)

            rendered_scenes.append(
                VoiceSceneRender(
                    scene_number=scene.scene_number,
                    purpose=scene.purpose,
                    narration=scene.narration,
                    audio_path=audio_path,
                )
            )

        logger.info(
            "Rendered %s voice scenes for package '%s'.",
            len(rendered_scenes),
            package.title,
        )

        return VoiceRenderResult(
            title=package.title,
            output_dir=self.output_dir,
            scenes=rendered_scenes,
        )

    def _render_scene(
        self,
        scene: VideoScene,
        audio_path: Path,
    ) -> None:
        narration = scene.narration.strip()

        if not narration:
            raise ValueError(
                f"Scene {scene.scene_number} narration cannot be empty."
            )

        command = self._build_command(narration, audio_path)

        for attempt in range(1, self.max_attempts + 1):
            logger.info(
                "Rendering TTS for scene %s/%s to %s.",
                scene.scene_number,
                attempt,
                audio_path,
            )

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired as exc:
                if attempt == self.max_attempts:
                    raise VoiceRenderError(
                        f"OpenClaw TTS timed out for scene "
                        f"{scene.scene_number}."
                    ) from exc

                logger.warning(
                    "OpenClaw TTS timed out for scene %s; retrying.",
                    scene.scene_number,
                )
                self._sleep_before_retry()
                continue

            if result.returncode == 0 and self._is_valid_wav(audio_path):
                logger.info(
                    "Rendered TTS for scene %s to %s.",
                    scene.scene_number,
                    audio_path,
                )
                return

            error = result.stderr.strip() or result.stdout.strip()

            if result.returncode == 0:
                error = (
                    "OpenClaw completed but WAV output was not created: "
                    f"{audio_path}"
                )

            if attempt == self.max_attempts:
                raise VoiceRenderError(
                    f"OpenClaw TTS failed for scene "
                    f"{scene.scene_number}: {error}"
                )

            logger.warning(
                "OpenClaw TTS failed for scene %s on attempt %s: %s",
                scene.scene_number,
                attempt,
                error,
            )
            self._sleep_before_retry()

    @staticmethod
    def _build_command(
        narration: str,
        audio_path: Path,
    ) -> list[str]:
        return [
            "openclaw",
            "infer",
            "tts",
            "convert",
            "--text",
            narration,
            "--output",
            str(audio_path),
        ]

    def _audio_path_for(self, scene: VideoScene) -> Path:
        purpose = _slugify(scene.purpose)

        return self.output_dir / (
            f"scene_{scene.scene_number:02d}_{purpose}.wav"
        )

    @staticmethod
    def _is_valid_wav(audio_path: Path) -> bool:
        return audio_path.is_file() and audio_path.suffix.lower() == ".wav"

    def _sleep_before_retry(self) -> None:
        if self.retry_delay_seconds > 0:
            time.sleep(self.retry_delay_seconds)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    slug = slug.strip("_")

    return slug or "scene"
