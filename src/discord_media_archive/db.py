from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, sessionmaker

from discord_media_archive.models import Base, ChannelScanState, MediaFile, Message


def create_db_engine(database_url: str):
    if database_url.startswith("sqlite:///"):
        db_path = Path(database_url.removeprefix("sqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    return create_engine(database_url, future=True)


def create_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def insert_message(session: Session, values: dict) -> None:
    stmt = sqlite_insert(Message).values(**values).prefix_with("OR IGNORE")
    session.execute(stmt)


def insert_media_file(session: Session, values: dict) -> None:
    stmt = sqlite_insert(MediaFile).values(**values).prefix_with("OR IGNORE")
    session.execute(stmt)


def commit_batch(session: Session) -> None:
    session.commit()
    session.expunge_all()

def get_channel_checkpoint_message_id(session: Session, channel_id: int) -> str | None:
    stmt = select(ChannelScanState.last_message_id).where(
        ChannelScanState.channel_id == str(channel_id)
    )
    return session.execute(stmt).scalar_one_or_none()

def upsert_channel_checkpoint(
    session: Session,
    *,
    channel_id: int,
    last_message_id: int,
) -> None:
    stmt = (
        sqlite_insert(ChannelScanState)
        .values(
            channel_id=str(channel_id),
            last_message_id=str(last_message_id),
            updated_at=datetime.now(timezone.utc),
        )
        .on_conflict_do_update(
            index_elements=[ChannelScanState.channel_id],
            set_={
                "last_message_id": str(last_message_id),
                "updated_at": datetime.now(timezone.utc),
            },
        )
    )
    session.execute(stmt)
