import os, pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# токен для внешнего клиента в тестах не используется (замокаем), но зададим для явности
os.environ.setdefault("SUPERHERO_TOKEN", "test-token")

from app.main import app, get_db
from app.models.base import Base

POSTGRES_TEST_DSN = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://heroes:heroes@db:5432/heroes_test",
)

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    eng = create_async_engine(POSTGRES_TEST_DSN, future=True)
    # Схему создаём миграциями: alembic upgrade head (см. README)
    yield eng
    await eng.dispose()

@pytest_asyncio.fixture()
async def async_session(test_engine):
    Session = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with Session() as session:
        yield session

@pytest_asyncio.fixture()
async def client(async_session):
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Глобальный стаб внешнего клиента (на случай порядка инициализации)
@pytest.fixture(autouse=True)
def stub_superhero_fetch(monkeypatch):
    from app.clients import superhero as client_mod
    async def fake_fetch(name: str):
        if name.lower() == "batman":
            return {"name": "Batman", "intelligence": 100, "strength": 26, "speed": 27, "power": 47}
        raise client_mod.SuperheroNotFound(name)
    monkeypatch.setattr(client_mod, "fetch_powerstats_by_name", fake_fetch)


