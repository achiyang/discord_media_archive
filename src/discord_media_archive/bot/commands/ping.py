from __future__ import annotations

from discord_media_archive.bot.logger import log

import discord
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


def register_command(
    client: ArchiveClient,
) -> None:
    guild_obj = discord.Object(id=client.settings.target_guild_id)

    @client.tree.command(
        name="ping",
        description="봇 응답 상태를 확인합니다.",
        guild=guild_obj,
    )
    async def ping_command(interaction: discord.Interaction) -> None:
        if interaction.guild_id != client.settings.target_guild_id:
            await interaction.response.send_message(
                "대상 길드에서만 사용할 수 있습니다.",
                ephemeral=True,
            )
            return

        latency_ms = round(client.latency * 1000, 2)

        await interaction.response.send_message(
            f"Pong! latency={latency_ms}ms",
            ephemeral=True,
        )

        await log(
            client,
            f"ping requested by user_id={interaction.user.id} latency={latency_ms}ms",
        )
