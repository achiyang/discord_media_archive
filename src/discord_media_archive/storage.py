from __future__ import annotations

import asyncio
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import mimetypes

import discord


@dataclass(frozen=True)
class SavedFile:
    storage_path: str
    sha256_hex: str


def is_media_attachment(attachment: discord.Attachment) -> bool:
    content_type = attachment.content_type or ""
    return content_type.startswith("image/") or content_type.startswith("video/")


def guess_extension(filename: str | None, content_type: str | None) -> str | None:
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix:
            return suffix.lstrip(".")

    if content_type:
        ext = mimetypes.guess_extension(content_type, strict=False)
        if ext:
            return ext.lstrip(".")

    return None


def build_storage_path(
    *,
    media_root: Path,
    guild_id: int,
    channel_id: int,
    created_at,
    attachment_id: int,
    filename: str | None,
    content_type: str | None,
) -> Path:
    year = f"{created_at.year:04d}"
    month = f"{created_at.month:02d}"
    ext = guess_extension(filename, content_type)
    basename = f"{attachment_id}.{ext}" if ext else str(attachment_id)
    return (
        media_root
        / year
        / month
        / f"guild_{guild_id}"
        / f"channel_{channel_id}"
        / basename
    )


def hash_file(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


async def save_attachment(
    *,
    media_root: Path,
    guild_id: int,
    channel_id: int,
    created_at,
    attachment: discord.Attachment,
) -> SavedFile:
    destination = build_storage_path(
        media_root=media_root,
        guild_id=guild_id,
        channel_id=channel_id,
        created_at=created_at,
        attachment_id=attachment.id,
        filename=attachment.filename,
        content_type=attachment.content_type,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with destination.open("wb") as file:
            await attachment.save(file, use_cached=False)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    sha256_hex = await asyncio.to_thread(hash_file, destination)

    return SavedFile(
        storage_path=str(destination),
        sha256_hex=sha256_hex,
    )
