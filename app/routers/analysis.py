from http import HTTPStatus
from typing import Annotated

import numpy as np
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.database import get_session
from app.models import Cliente, LogAnalise
from app.schemas import PredicaoRisco, TransacaoEntrada
from app.security import get_current_user

router = APIRouter(prefix='/analysis', tags=['analysis'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[Cliente, Depends(get_current_user)]

FEATURE_COLUMNS = [
    'amount',
    'oldbalanceOrg',
    'newbalanceOrig',
    'oldbalanceDest',
    'newbalanceDest',
    'diferenca_saldo_orig',
    'diferenca_saldo_dest',
    'type_CASH_IN',
    'type_CASH_OUT',
    'type_DEBIT',
    'type_PAYMENT',
    'type_TRANSFER',
]

TRANSACTION_TYPES = [
    'CASH_IN',
    'CASH_OUT',
    'DEBIT',
    'PAYMENT',
    'TRANSFER',
]


def build_feature_vector(transacao: TransacaoEntrada) -> np.ndarray:
    diferenca_saldo_orig = transacao.oldbalanceOrg - transacao.newbalanceOrig
    diferenca_saldo_dest = transacao.newbalanceDest - transacao.oldbalanceDest

    type_encoded = {
        f'type_{t}': 1.0 if transacao.type == t else 0.0
        for t in TRANSACTION_TYPES
    }

    features = {
        'amount': transacao.amount,
        'oldbalanceOrg': transacao.oldbalanceOrg,
        'newbalanceOrig': transacao.newbalanceOrig,
        'oldbalanceDest': transacao.oldbalanceDest,
        'newbalanceDest': transacao.newbalanceDest,
        'diferenca_saldo_orig': diferenca_saldo_orig,
        'diferenca_saldo_dest': diferenca_saldo_dest,
        **type_encoded,
    }

    vector = np.array([[features[col] for col in FEATURE_COLUMNS]])
    return vector


@router.post(
    '/analisar/', status_code=HTTPStatus.CREATED, response_model=PredicaoRisco
)
async def solicitar_analise(
    request: Request,
    session: T_Session,
    transacao: TransacaoEntrada,
    cliente: T_CurrentUser,
):
    model = request.app.state.model
    scaler = request.app.state.scaler

    feature_vector = build_feature_vector(transacao)
    feature_vector_scaled = scaler.transform(feature_vector)

    is_fraud = bool(model.predict(feature_vector_scaled)[0])
    risk_score = float(model.predict_proba(feature_vector_scaled)[0][1])

    db_log = LogAnalise(
        dados_entrada=transacao.model_dump_json(),
        predicao_retornada=f'is_fraud: {is_fraud}, score: {risk_score}',
        cliente_id=cliente.id,
    )

    session.add(db_log)
    await session.commit()
    await session.refresh(db_log)

    return {
        'analysis_id': db_log.id_log,
        'is_fraud': is_fraud,
        'risk_score': risk_score,
    }


@router.get('/historico', response_model=list[schemas.LogAnalise])
async def obter_historico(session: T_Session, cliente: T_CurrentUser):
    query = select(LogAnalise).where(LogAnalise.cliente_id == cliente.id)
    result = await session.execute(query)
    return result.scalars().all()
