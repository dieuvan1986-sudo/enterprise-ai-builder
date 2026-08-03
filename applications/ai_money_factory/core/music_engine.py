from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

MusicFitMode = Literal["trim", "loop"]


@dataclass(slots=True)
class MusicRenderConfig:
    """
    Configuration for preparing one local background music artifact.
    """

    source_path: Path | str
    output_dir: Path | str
    target_duration_seconds: float
    title: str = "music"
    fit_mode: MusicFitMode = "loop"
    output_filename: str | None = None
    ffmpeg_path: Path | str = "ffmpeg"
    sample_rate_hz: int = 48_000
    channels: int = 2
    volume: float = 0.18
    timeout_seconds: int = 120


@dataclass(slots=True)
class MusicTrack:
    """
    Normalized background music artifact for downstream video composition.
    """

    title: str
    source_path: Path
    audio_path: Path
    duration_seconds: float
    fit_mode: MusicFitMode


class MusicEngineError(RuntimeError):
    """
    Raised when a local music file cannot be prepared for composition.
    """


class MusicEngine:
    """
    Prepare existing local music for the AI Money Factory video composer.

    This engine does not generate music. It validates a caller-provided local
    file and uses ffmpeg to export a normalized WAV artifact at the requested
    target duration.
    """

    _SUPPORTED_EXTENSIONS = {
        ".aac",
        ".aiff",
        ".flac",
        ".m4a",
        ".mp3",
        ".ogg",
        ".opus",
        ".wav",
    }

    def render(self, config: MusicRenderConfig) -> MusicTrack:
        source_path = Path(config.source_path)
        output_dir = Path(config.output_dir)
        target_duration = _validated_duration(config.target_duration_seconds)

        self._validate_config(config=config, source_path=source_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = self._output_path_for(config, output_dir)

        logger.info(
            "Rendering music '%s' from %s to %s using %s mode.",
            config.title,
            source_path,
            audio_path,
            config.fit_mode,
        )

        command = self._build_command(
            config=config,
            source_path=source_path,
            output_path=audio_path,
            target_duration_seconds=target_duration,
        )
        self._run_ffmpeg(command, config.timeout_seconds, audio_path)

        logger.info(
            "Rendered normalized music artifact '%s' at %s seconds.",
            audio_path,
            target_duration,
        )

        return MusicTrack(
            title=config.title,
            source_path=source_path,
            audio_path=audio_path,
            duration_seconds=target_duration,
            fit_mode=config.fit_mode,
        )

    def _validate_config(
        self,
        *,
        config: MusicRenderConfig,
        source_path: Path,
    ) -> None:
        if config.fit_mode not in ("trim", "loop"):
            raise ValueError("fit_mode must be either 'trim' or 'loop'.")

        if not source_path.is_file():
            raise FileNotFoundError(f"Music source file does not exist: {source_path}")

        if source_path.suffix.lower() not in self._SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported music source extension: {source_path.suffix}"
            )

        if config.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive.")

        if config.channels <= 0:
            raise ValueError("channels must be positive.")

        if config.volume <= 0:
            raise ValueError("volume must be positive.")

        if config.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1.")

    def _build_command(
        self,
        *,
        config: MusicRenderConfig,
        source_path: Path,
        output_path: Path,
        target_duration_seconds: float,
    ) -> list[str]:
        command = [
            str(config.ffmpeg_path),
            "-y",
            "-stream_loop",
            "-1" if config.fit_mode == "loop" else "0",
            "-i",
            str(source_path),
            "-t",
            _format_seconds(target_duration_seconds),
            "-vn",
            "-ac",
            str(config.channels),
            "-ar",
            str(config.sample_rate_hz),
            "-af",
            f"volume={config.volume}",
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]

        if config.fit_mode == "trim":
            del command[2:4]

        return command

    @staticmethod
    def _run_ffmpeg(
        command: list[str],
        timeout_seconds: int,
        audio_path: Path,
    ) -> None:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise MusicEngineError("ffmpeg timed out while rendering music.") from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            raise MusicEngineError(f"ffmpeg failed while rendering music: {error}")

        if not audio_path.is_file():
            raise MusicEngineError(
                f"ffmpeg completed but output was not created: {audio_path}"
            )

    @staticmethod
    def _output_path_for(
        config: MusicRenderConfig,
        output_dir: Path,
    ) -> Path:
        filename = config.output_filename

        if filename is None:
            filename = f"{_slugify(config.title)}_music.wav"

        output_path = output_dir / filename

        if output_path.suffix.lower() != ".wav":
            raise ValueError("Music output artifact must use a .wav filename.")

        return output_path


def _validated_duration(duration_seconds: float) -> float:
    if duration_seconds <= 0:
        raise ValueError("target_duration_seconds must be positive.")

    return float(duration_seconds)


def _format_seconds(duration_seconds: float) -> str:
    return f"{duration_seconds:.3f}".rstrip("0").rstrip(".")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    slug = slug.strip("_")

    return slug or "music"
