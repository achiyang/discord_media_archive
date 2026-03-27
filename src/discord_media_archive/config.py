from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    target_guild_id: int
    database_url: str
    media_root: Path
    log_channel_id: int
    admin_user_id: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    return Settings(
        discord_bot_token=_require_env("DISCORD_BOT_TOKEN"),
        target_guild_id=int(_require_env("TARGET_GUILD_ID")),
        database_url=_require_env("DATABASE_URL"),
        media_root=Path(_require_env("MEDIA_ROOT")),
        log_channel_id=int(_require_env("LOG_CHANNEL_ID")),
        admin_user_id=int(_require_env("ADMIN_USER_ID")),
    )
