from __future__ import annotations

import asyncio

import discord

from discord_media_archive.config import Settings
from discord_media_archive.db import commit_batch, upsert_channel_checkpoint
from discord_media_archive.bot.backfill import run_startup_backfill
from discord_media_archive.bot.command_system.registry import register_commands
from discord_media_archive.bot.logger import log
from discord_media_archive.bot.message_handler import process_message


class ArchiveClient(discord.Client):
    def __init__(self, *, settings: Settings, session_factory) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        super().__init__(intents=intents)
        self.settings = settings
        self.session_factory = session_factory
        self._startup_backfill_task: asyncio.Task | None = None
        self._startup_backfill_started = False
        self._log_channel = None
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        guild_obj = discord.Object(id=self.settings.target_guild_id)

        self.tree.clear_commands(guild=guild_obj)
        register_commands(self)

        await self.tree.sync(guild=guild_obj)

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} ({self.user.id})")
        await log(self, f"Logged in as {self.user} ({self.user.id})")

        if self._startup_backfill_started:
            return

        self._startup_backfill_started = True
        self._startup_backfill_task = asyncio.create_task(run_startup_backfill(self))

    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.guild.id != self.settings.target_guild_id:
            return
        if message.author.bot:
            return

        with self.session_factory() as session:
            message_delta, media_delta = await process_message(self, session, message)

            upsert_channel_checkpoint(
                session=session,
                channel_id=message.channel.id,
                last_message_id=message.id,
            )

            commit_batch(session)

            if message_delta:
                commit_batch(session)
                await log(
                    self,
                    f"[live] channel={getattr(message.channel, 'name', message.channel.id)} "
                    f"message_id={message.id} saved_messages={message_delta} saved_media={media_delta}",
                )
