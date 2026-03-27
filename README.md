# Discord Media Archive

A small Discord media archiver built with `discord.py`.

## What it does
- Connects as a bot
- Walks every text channel in one guild
- Reads message history from oldest to newest
- Saves only image/video attachments
- Stores message metadata in SQLite
- Stores files under `media/YYYY/MM/guild_<id>/channel_<id>/`

## Setup
1. Create and activate a virtualenv
2. Copy `.env.example` to `.env` and fill in values
3. Install:
   ```bash
   pip install -e .
   ```
4. Run:
   ```bash
   python scripts/backfill_guild.py
   ```

## Notes
- Enable the Message Content intent in the Discord developer portal if you want message text saved reliably.
- This tool is intentionally sequential and conservative.
