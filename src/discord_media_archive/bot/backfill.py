from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
from sqlalchemy.orm import Session

from discord_media_archive.bot.logger import log
from discord_media_archive.bot.message_handler import process_message
from discord_media_archive.db import (
    commit_batch,
    get_channel_checkpoint_message_id,
    upsert_channel_checkpoint,
)

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


async def run_startup_backfill(client: ArchiveClient) -> None:
    try:
        guild = client.get_guild(client.settings.target_guild_id)
        if guild is None:
            raise RuntimeError(f"Guild not found in cache: {client.settings.target_guild_id}")

        text_channels = [
            c for c in guild.text_channels
            if c.permissions_for(guild.me).read_message_history
        ]
        text_channels.sort(key=lambda c: (c.position, c.id))

        total_messages = 0
        total_media = 0

        with client.session_factory() as session:
            for channel in text_channels:
                try:
                    after_message_id = get_channel_checkpoint_message_id(session, channel.id)

                    if after_message_id is None:
                        await log(client, f"[resume] channel={channel.name} checkpoint=None (full scan)")
                    else:
                        await log(
                            client,
                            f"[resume] channel={channel.name} checkpoint={after_message_id}",
                        )

                    message_count, media_count = await backfill_channel(
                        client,
                        session=session,
                        channel=channel,
                        after_message_id=after_message_id,
                    )
                    total_messages += message_count
                    total_media += media_count

                    await log(
                        client,
                        f"[done] channel={channel.name} "
                        f"saved_messages={message_count} "
                        f"saved_media={media_count}",
                    )
                except Exception as exc:
                    session.rollback()
                    session.expunge_all()
                    await log(
                        client,
                        f"[channel-backfill-error] "
                        f"channel={channel.name} "
                        f"channel_id={channel.id} "
                        f"error_type={type(exc).__name__} "
                        f"error={exc!r}",
                    )

        await log(
            client,
            f"[startup-backfill-complete] "
            f"saved_messages={total_messages} saved_media={total_media}",
        )
    except Exception as exc:
        await log(
            client,
            f"[startup-backfill-fatal] "
            f"error_type={type(exc).__name__} "
            f"error={exc!r}",
        )
        raise


async def backfill_channel(
    client: ArchiveClient,
    session: Session,
    channel: discord.TextChannel,
    *,
    after_message_id: str | None,
    commit_every: int = 100,
) -> tuple[int, int]:
    saved_messages = 0
    saved_media_files = 0
    pending_writes = 0
    scanned_messages = 0
    last_seen_message_id: int | None = None

    history_kwargs: dict[str, Any] = {
        "limit": None,
        "oldest_first": True,
    }
    if after_message_id is not None:
        history_kwargs["after"] = discord.Object(id=int(after_message_id))

    async for message in channel.history(**history_kwargs):
        scanned_messages += 1
        last_seen_message_id = message.id

        message_delta, media_delta = await process_message(client, session, message)

        if message_delta:
            saved_messages += message_delta
            saved_media_files += media_delta
            pending_writes += 1

        if scanned_messages % 1000 == 0:
            await log(client, f"[scan] channel={channel.name} scanned={scanned_messages}")

        if pending_writes >= commit_every:
            commit_batch(session)
            pending_writes = 0
            await log(
                client,
                f"[progress] channel={channel.name} "
                f"scanned={scanned_messages} "
                f"saved_messages={saved_messages} "
                f"saved_media={saved_media_files}",
            )

    if pending_writes:
        commit_batch(session)

    if last_seen_message_id is not None:
        upsert_channel_checkpoint(
            session,
            channel_id=channel.id,
            last_message_id=last_seen_message_id,
        )
        commit_batch(session)

    return saved_messages, saved_media_files
