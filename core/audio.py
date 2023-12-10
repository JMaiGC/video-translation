import subprocess
import warnings
from pathlib import Path

import whisper
from loguru import logger

from config import DOWNLOAD_DIR, FFMPEG_BIN, FFMPEG_OPTS, WHISPER_MODEL_NAME
from core.utils import write_srt

model = whisper.load_model(WHISPER_MODEL_NAME)


def generate_srt(audio: str) -> list[list[str]]:
    warnings.filterwarnings("ignore")
    result = model.transcribe(audio)
    source_language = result["language"]
    if source_language == "en":
        dist_language = "zh"
    else:
        dist_language = "en"

    srts = [[write_srt(result["segments"], audio, source_language), source_language]]
    logger.info(f"Generate {source_language} srt: {srts[0][0]}")
    result = model.transcribe(audio, language=dist_language)
    srts.append([write_srt(result["segments"], audio, dist_language), dist_language])
    warnings.filterwarnings("default")
    logger.info(f"Generate {dist_language} srt: {srts[1][0]}")
    return srts


def generate_audio(video: str | Path, suffix=".mp3") -> str:
    if not isinstance(video, Path):
        video = Path(video)

    audio = f"{DOWNLOAD_DIR}/{video.parts[-1].removesuffix(video.suffix)}{suffix}"

    subprocess.check_call(
        f"{FFMPEG_BIN} {FFMPEG_OPTS} -i '{video.as_posix()}' -b:a 192K -vn '{audio}'",
        shell=True,
    )
    logger.info(f"Audio generated: {audio}")
    return audio
