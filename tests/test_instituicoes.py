from http import HTTPStatus


async def test_criar_instituicao(client, token_admin):
    response = await client.post(
        '/instituicoes/',
        json={'nome_instituicao': 'Fintech A', 'cnpj': '11222333000181'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['nome_instituicao'] == 'Fintech A'
    assert data['ativo'] is True
    assert 'api_key' in data
    assert data['api_key'].startswith('fz_')


async def test_criar_instituicao_cnpj_invalido(client, token_admin):
    response = await client.post(
        '/instituicoes/',
        json={'nome_instituicao': 'Fintech B', 'cnpj': '00000000000000'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_criar_instituicao_cnpj_duplicado(client, token_admin):
    payload = {'nome_instituicao': 'Fintech C', 'cnpj': '11222333000181'}
    await client.post(
        '/instituicoes/',
        json=payload,
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    response = await client.post(
        '/instituicoes/',
        json={'nome_instituicao': 'Fintech D', 'cnpj': '11222333000181'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_listar_instituicoes(
    client, token_admin, instituicao_cadastrada
):
    response = await client.get(
        '/instituicoes/',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) >= 1


async def test_buscar_instituicao_por_id(
    client, token_admin, instituicao_cadastrada
):
    id_ = instituicao_cadastrada['id']
    response = await client.get(
        f'/instituicoes/{id_}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == id_


async def test_buscar_instituicao_inexistente(client, token_admin):
    response = await client.get(
        '/instituicoes/id-que-nao-existe',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_alterar_status_instituicao(
    client, token_admin, instituicao_cadastrada
):
    id_ = instituicao_cadastrada['id']
    response = await client.patch(
        f'/instituicoes/{id_}/status',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['ativo'] is False


async def test_deletar_instituicao(
    client, token_admin, instituicao_cadastrada
):
    id_ = instituicao_cadastrada['id']
    response = await client.delete(
        f'/instituicoes/{id_}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_instituicao_nao_acessa_rota_admin(client, token_instituicao):
    """Token de instituição não deve acessar rotas administrativas."""
    response = await client.get(
        '/instituicoes/',
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
