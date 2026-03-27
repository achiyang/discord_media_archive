from __future__ import annotations

import discord

from discord_media_archive.bot.client import ArchiveClient
from discord_media_archive.bot.commands.checks import admin_only
from discord_media_archive.bot.logger import log


def register_command(client: ArchiveClient) -> None:
    guild_obj = discord.Object(id=client.settings.target_guild_id)

    @client.tree.command(
        name="shutdown_bot",
        description="봇을 종료합니다.",
        guild=guild_obj,
    )
    @admin_only(client)
    async def shutdown_command(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "봇을 종료합니다.",
            ephemeral=True,
        )
        await log(client, f"shutdown requested by user_id={interaction.user.id}")
        await client.close()
