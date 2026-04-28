from http import HTTPStatus
from unittest.mock import MagicMock

import numpy as np
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import table_registry
from app.settings import Settings

# Banco de dados em memória exclusivo para testes
DATABASE_URL_TEST = 'sqlite+aiosqlite:///:memory:'


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        DATABASE_URL_TEST,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    # Mock do modelo ML
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
async def instituicao_cadastrada(client):
    """Cria uma instituição e retorna seus dados incluindo a api_key."""
    response = await client.post(
        '/instituicoes/',
        json={
            'nome_instituicao': 'Banco Teste',
            'cnpj': '11222333000181',
        },
        headers={'Authorization': f'Bearer {await _get_admin_token(client)}'},
    )
    return response.json()


@pytest_asyncio.fixture
async def token_instituicao(client, instituicao_cadastrada):
    """Retorna um token JWT válido para a instituição de teste."""
    response = await client.post(
        '/auth/login',
        data={
            'username': instituicao_cadastrada['cnpj'],
            'password': instituicao_cadastrada['api_key'],
        },
    )
    return response.json()['access_token']


async def _get_admin_token(client):
    settings = Settings()

    response = await client.post(
        '/auth/admin/login',
        data={
            'username': settings.ADMIN_USERNAME,
            'password': settings.ADMIN_PASSWORD,
        },
    )

    assert response.status_code == HTTPStatus.OK, (
        f'Erro ao logar admin no teste: {response.json()}'
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def token_admin(client):
    return await _get_admin_token(client)
