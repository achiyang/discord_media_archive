from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


async def get_log_channel(client: ArchiveClient):
    if client._log_channel is not None:
        return client._log_channel

    channel = client.get_channel(client.settings.log_channel_id)
    if channel is None:
        channel = await client.fetch_channel(client.settings.log_channel_id)

    client._log_channel = channel
    return channel


async def log(client: ArchiveClient, message: str) -> None:
    try:
        channel = await get_log_channel(client)
        await channel.send(message, suppress_embeds=True)
    except Exception as exc:
        print(f"[log-fallback] failed to send log: {exc!r}")
        print(message)
