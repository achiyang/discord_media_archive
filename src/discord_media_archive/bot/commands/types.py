from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


class CommandModule(Protocol):
    def register_command(self, client: ArchiveClient) -> None:
        ...