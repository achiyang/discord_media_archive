from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

import discord_media_archive.bot.commands as commands_pkg
from discord_media_archive.bot.command_system.types import CommandRegistrar

if TYPE_CHECKING:
    from discord_media_archive.bot.client import ArchiveClient


def _discover_command_registrars() -> list[CommandRegistrar]:
    discovered: list[CommandRegistrar] = []

    for module_info in pkgutil.iter_modules(commands_pkg.__path__):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        full_name = f"{commands_pkg.__name__}.{module_name}"
        module = importlib.import_module(full_name)

        register = getattr(module, "register_command", None)
        if register is None or not callable(register):
            raise RuntimeError(
                f"Command module '{full_name}' must define "
                "callable register_command(client)"
            )

        discovered.append(register)

    discovered.sort(key=lambda register: register.__module__)
    return discovered


def register_commands(client: ArchiveClient) -> None:
    for register in _discover_command_registrars():
        register(client)
