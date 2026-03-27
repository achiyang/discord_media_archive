from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps

import discord

from discord_media_archive.bot.client import ArchiveClient

InteractionHandler = Callable[[discord.Interaction], Awaitable[None]]


def admin_only(
    client: ArchiveClient,
) -> Callable[[InteractionHandler], InteractionHandler]:
    def decorator(func: InteractionHandler) -> InteractionHandler:
        @wraps(func)
        async def wrapper(interaction: discord.Interaction) -> None:
            if interaction.user.id != client.settings.admin_user_id:
                await interaction.response.send_message(
                    "이 명령어를 사용할 권한이 없습니다.",
                    ephemeral=True,
                )
                return

            await func(interaction)

        return wrapper

    return decorator
