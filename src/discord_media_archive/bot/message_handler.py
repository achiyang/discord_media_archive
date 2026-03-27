from __future__ import annotations

import asyncio
from datetime import timezone
from typing import TYPE_CHECKING, Any

import discord
from sqlalchemy.orm import Session

from discord_media_archive.db import insert_media_file, insert_message
from discord_media_archive.storage import is_media_attachment, save_attachment
from discord_media_archive.bot.logger import log

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


async def save_attachment_task(
    client: ArchiveClient,
    *,
    message: discord.Message,
    attachment: discord.Attachment,
) -> tuple[discord.Attachment, Any]:
    if message.guild is None:
        raise RuntimeError(f"Message has no guild: message_id={message.id}")

    saved = await save_attachment(
        media_root=client.settings.media_root,
        guild_id=message.guild.id,
        channel_id=message.channel.id,
        created_at=message.created_at,
        attachment=attachment,
    )
    return attachment, saved


async def process_message(
    client: ArchiveClient,
    session: Session,
    message: discord.Message,
) -> tuple[int, int]:
    if message.guild is None:
        return 0, 0

    media_attachments = [
        attachment for attachment in message.attachments
        if is_media_attachment(attachment)
    ]
    if not media_attachments:
        return 0, 0

    tasks = [
        save_attachment_task(client, message=message, attachment=attachment)
        for attachment in media_attachments
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    media_rows: list[dict[str, Any]] = []

    for attachment, result in zip(media_attachments, results):
        if isinstance(result, Exception):
            await log(
                client,
                f"[skip] channel={message.channel.name} "
                f"message_id={message.id} "
                f"attachment_id={attachment.id} "
                f"filename={attachment.filename} "
                f"error_type={type(result).__name__} "
                f"error={result!r}",
            )
            continue

        saved_attachment, saved = result
        media_rows.append(
            {
                "discord_attachment_id": str(saved_attachment.id),
                "message_id": str(message.id),
                "filename": saved_attachment.filename,
                "content_type": saved_attachment.content_type,
                "size_bytes": saved_attachment.size,
                "storage_path": saved.storage_path,
                "sha256": saved.sha256_hex,
            }
        )

    if not media_rows:
        return 0, 0

    insert_message(
        session,
        {
            "message_id": str(message.id),
            "guild_id": str(message.guild.id),
            "channel_id": str(message.channel.id),
            "author_id": str(message.author.id),
            "author_name": getattr(message.author, "name", None),
            "content": message.content,
            "created_at": message.created_at.astimezone(timezone.utc),
        },
    )

    for media_row in media_rows:
        insert_media_file(session, media_row)

    return 1, len(media_rows)
