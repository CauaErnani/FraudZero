from http import HTTPStatus

from app.settings import Settings


async def test_admin_login_sucesso(client):
    settings = Settings()
    response = await client.post(
        '/auth/admin/login',
        data={
            'username': settings.ADMIN_USERNAME,
            'password': settings.ADMIN_PASSWORD,
        },
    )
    assert response.status_code == HTTPStatus.OK


async def test_admin_login_credenciais_erradas(client):
    response = await client.post(
        '/auth/admin/login',
        data={'username': 'admin', 'password': 'senhaerrada'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_instituicao_login_sucesso(
    client, instituicao_cadastrada, token_admin
):
    response = await client.post(
        '/auth/login',
        data={
            'username': instituicao_cadastrada['cnpj'],
            'password': instituicao_cadastrada['api_key'],
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()


async def test_instituicao_login_api_key_errada(
    client, instituicao_cadastrada
):
    response = await client.post(
        '/auth/login',
        data={
            'username': instituicao_cadastrada['cnpj'],
            'password': 'chave_errada',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_me_retorna_dados_instituicao(client, token_instituicao):
    response = await client.get(
        '/auth/me',
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['nome_instituicao'] == 'Banco Teste'


async def test_token_admin_nao_acessa_me(client, token_admin):
    """Token de admin não deve funcionar no endpoint de instituição."""
    response = await client.get(
        '/auth/me',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
