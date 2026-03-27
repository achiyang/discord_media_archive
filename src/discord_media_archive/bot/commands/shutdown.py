from __future__ import annotations

import discord

from discord_media_archive.bot.logger import log
from discord_media_archive.bot.client import ArchiveClient


def register_command(client: ArchiveClient) -> None:
    guild_obj = discord.Object(id=client.settings.target_guild_id)

    @client.tree.command(
        name="shutdown_bot",
        description="봇을 종료합니다.",
        guild=guild_obj,
    )
    async def shutdown_command(interaction: discord.Interaction) -> None:
        if interaction.guild_id != client.settings.target_guild_id:
            await interaction.response.send_message(
                "대상 길드에서만 사용할 수 있습니다.",
                ephemeral=True,
            )
            return

        if interaction.user.id != client.settings.admin_user_id:
            await interaction.response.send_message(
                "이 명령어를 사용할 권한이 없습니다.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "봇을 종료합니다.",
            ephemeral=True,
        )
        await log(client, f"shutdown requested by user_id={interaction.user.id}")
        await client.close()
