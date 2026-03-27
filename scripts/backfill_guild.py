from discord_media_archive.bot.client import ArchiveClient
from discord_media_archive.config import load_settings
from discord_media_archive.db import create_db_engine, create_session_factory, init_db


def main() -> None:
    settings = load_settings()
    settings.media_root.mkdir(parents=True, exist_ok=True)

    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    init_db(engine)

    client = ArchiveClient(settings=settings, session_factory=session_factory)
    client.run(settings.discord_bot_token, log_handler=None)


if __name__ == "__main__":
    main()
