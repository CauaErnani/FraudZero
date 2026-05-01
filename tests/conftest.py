from unittest.mock import MagicMock

import numpy as np
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database import get_session
from app.main import app
from app.models import table_registry
from app.settings import Settings

settings = Settings()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0])
    mock_model.predict_proba.return_value = np.array([[0.95, 0.05]])

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    app.state.model = mock_model

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def instituicao_cadastrada(client, token_admin):
    response = await client.post(
        '/instituicoes/',
        json={
            'nome_instituicao': 'Banco Teste',
            'cnpj': '11222333000181',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    return response.json()


@pytest_asyncio.fixture
async def token_instituicao(client, instituicao_cadastrada):
    response = await client.post(
        '/auth/login',
        data={
            'username': instituicao_cadastrada['cnpj'],
            'password': instituicao_cadastrada['api_key'],
        },
    )
    return response.json()['access_token']


async def _get_admin_token(client: AsyncClient) -> str:
    response = await client.post(
        '/auth/admin/login',
        data={
            'username': settings.ADMIN_USERNAME,
            'password': settings.ADMIN_PASSWORD,
        },
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def token_admin(client):
    return await _get_admin_token(client)
