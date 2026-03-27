from __future__ import annotations

import discord

from discord_media_archive.bot.logger import log
from discord_media_archive.bot.client import ArchiveClient


def register_command(client: ArchiveClient) -> None:
    guild_obj = discord.Object(id=client.settings.target_guild_id)

    @client.tree.command(
        name="ping",
        description="봇 응답 상태를 확인합니다.",
        guild=guild_obj,
    )
    async def ping_command(interaction: discord.Interaction) -> None:
        latency_ms = round(client.latency * 1000, 2)

        await interaction.response.send_message(
            f"Pong! latency={latency_ms}ms",
            ephemeral=True,
        )

        await log(
            client,
            f"ping requested by user_id={interaction.user.id} latency={latency_ms}ms",
        )
