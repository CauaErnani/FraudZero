from http import HTTPStatus

TRANSACAO_VALIDA = {
    'transaction_id': 'txn_001',
    'user_id': 'usr_001',
    'type': 'TRANSFER',
    'amount': 1500.00,
    'oldbalanceOrg': 5000.00,
    'newbalanceOrig': 3500.00,
    'oldbalanceDest': 1000.00,
    'newbalanceDest': 2500.00,
}


async def test_analisar_transacao(client, token_instituicao):
    response = await client.post(
        '/analysis/analisar/',
        json=TRANSACAO_VALIDA,
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert 'analysis_id' in data
    assert isinstance(data['is_fraud'], bool)
    assert 0.0 <= data['risk_score'] <= 1.0


async def test_analisar_tipo_invalido(client, token_instituicao):
    transacao = {**TRANSACAO_VALIDA, 'type': 'TIPO_INVALIDO'}
    response = await client.post(
        '/analysis/analisar/',
        json=transacao,
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_analisar_valor_negativo(client, token_instituicao):
    transacao = {**TRANSACAO_VALIDA, 'amount': -100.00}
    response = await client.post(
        '/analysis/analisar/',
        json=transacao,
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_historico_retorna_logs(client, token_instituicao):
    await client.post(
        '/analysis/analisar/',
        json=TRANSACAO_VALIDA,
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    response = await client.get(
        '/analysis/historico',
        headers={'Authorization': f'Bearer {token_instituicao}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) >= 1


async def test_historico_isolado_por_instituicao(client, token_admin, session):
    """Cada instituição só vê seus próprios logs."""
    inst_a = (
        await client.post(
            '/instituicoes/',
            json={'nome_instituicao': 'Banco A', 'cnpj': '11222333000181'},
            headers={'Authorization': f'Bearer {token_admin}'},
        )
    ).json()

    inst_b = (
        await client.post(
            '/instituicoes/',
            json={'nome_instituicao': 'Banco B', 'cnpj': '34238864000168'},
            headers={'Authorization': f'Bearer {token_admin}'},
        )
    ).json()

    token_a = (
        await client.post(
            '/auth/login',
            data={'username': inst_a['cnpj'], 'password': inst_a['api_key']},
        )
    ).json()['access_token']

    token_b = (
        await client.post(
            '/auth/login',
            data={'username': inst_b['cnpj'], 'password': inst_b['api_key']},
        )
    ).json()['access_token']

    await client.post(
        '/analysis/analisar/',
        json=TRANSACAO_VALIDA,
        headers={'Authorization': f'Bearer {token_a}'},
    )

    response = await client.get(
        '/analysis/historico',
        headers={'Authorization': f'Bearer {token_b}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0


async def test_analisar_sem_autenticacao(client):
    response = await client.post('/analysis/analisar/', json=TRANSACAO_VALIDA)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
