from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


class CommandRegistrar(Protocol):
    def __call__(self, client: ArchiveClient) -> None:
        ...