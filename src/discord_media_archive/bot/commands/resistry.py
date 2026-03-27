from __future__ import annotations

from typing import TYPE_CHECKING

from discord_media_archive.bot.commands import (
    shutdown,
    ping,
)

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient

COMMAND_MODULES = [
    shutdown,
    ping,
]


def register_commands(
    client: ArchiveClient,
) -> None:
    for module in COMMAND_MODULES:
        module.register_command(client)
