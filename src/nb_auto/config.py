from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str = "https://api.kie.ai"
    callback_url: str | None = None
    output_dir: Path = Path("outputs")
    db_path: Path = Path("outputs/tasks.sqlite3")
    default_aspect_ratio: str = "1:1"
    default_resolution: str = "1K"
    default_output_format: str = "png"


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("KIE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("KIE_API_KEY is missing. Put it in .env or your shell environment.")

    output_dir = Path(os.getenv("NB_OUTPUT_DIR", "outputs"))
    db_path = Path(os.getenv("NB_DB_PATH", str(output_dir / "tasks.sqlite3")))

    callback_url = os.getenv("KIE_CALLBACK_URL", "").strip() or None

    return Settings(
        api_key=api_key,
        base_url=os.getenv("KIE_BASE_URL", "https://api.kie.ai").rstrip("/"),
        callback_url=callback_url,
        output_dir=output_dir,
        db_path=db_path,
        default_aspect_ratio=os.getenv("NB_DEFAULT_ASPECT_RATIO", "1:1"),
        default_resolution=os.getenv("NB_DEFAULT_RESOLUTION", "1K"),
        default_output_format=os.getenv("NB_DEFAULT_OUTPUT_FORMAT", "png"),
    )
