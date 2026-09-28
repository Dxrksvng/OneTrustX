import os

os.environ["DATABASE_URL"] = "sqlite://"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.db import Base, get_db


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(main, "Session", factory)

    def db(request: __import__("fastapi").Request):
        with factory() as session:
            session.info["demo_session"] = request.headers.get("X-Demo-Session", "legacy")
            yield session

    main.app.dependency_overrides[get_db] = db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()
    engine.dispose()
