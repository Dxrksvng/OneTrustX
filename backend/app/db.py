import os
from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:////tmp/timetwin.db" if os.getenv("VERCEL") else "sqlite:///./timetwin.db",
)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    **({"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}),
)
Session = sessionmaker(engine, expire_on_commit=False)


def get_db(request: Request):
    key = request.headers.get("X-Demo-Session", "legacy")
    if key != "legacy":
        try:
            key = str(UUID(key))
        except ValueError:
            raise HTTPException(422, "Invalid demo session") from None
    with Session() as session:
        session.info["demo_session"] = key
        yield session
