from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING, cast

from discord_media_archive.bot.commands.types import CommandModule
import discord_media_archive.bot.commands as commands_pkg

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


_SKIP_MODULES = {"registry", "types", "__init__"}


def _discover_command_modules() -> list[CommandModule]:
    discovered: list[CommandModule] = []

    for module_info in pkgutil.iter_modules(commands_pkg.__path__):
        module_name = module_info.name

        if module_name.startswith("_") or module_name in _SKIP_MODULES:
            continue

        full_name = f"{commands_pkg.__name__}.{module_name}"
        module = importlib.import_module(full_name)

        register = getattr(module, "register_command", None)
        if register is None or not callable(register):
            raise RuntimeError(
                f"Command module '{full_name}' must define "
                f"callable register_command(client)"
            )

        discovered.append(cast(CommandModule, module))

    discovered.sort(key=lambda m: m.__name__)
    return discovered


def register_commands(client: ArchiveClient) -> None:
    for module in _discover_command_modules():
        module.register_command(client)
