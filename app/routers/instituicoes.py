import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.database import get_session
from app.models import Cliente
from app.schemas import ClienteCreateResponse, ClienteSchema
from app.security import get_current_admin, get_password_hash

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentAdmin = Annotated[str, Depends(get_current_admin)]

router = APIRouter(prefix='/instituicoes', tags=['instituicoes'])


@router.post('/', response_model=ClienteCreateResponse, status_code=201)
async def create_instituicao(
    instituicao: ClienteSchema,
    session: T_Session,
    _: T_CurrentAdmin,  # Apenas verifica que é admin, não usa o valor
):
    query_nome = select(Cliente).where(
        Cliente.nome_instituicao == instituicao.nome_instituicao
    )
    if await session.scalar(query_nome):
        raise HTTPException(
            status_code=400, detail='Nome da instituição já cadastrado.'
        )

    query_cnpj = select(Cliente).where(Cliente.cnpj == instituicao.cnpj)
    if await session.scalar(query_cnpj):
        raise HTTPException(status_code=400, detail='CNPJ já cadastrado.')

    plain_api_key = f'fz_{secrets.token_urlsafe(32)}'
    hashed_key = get_password_hash(plain_api_key)

    new_client = Cliente(
        nome_instituicao=instituicao.nome_instituicao,
        cnpj=instituicao.cnpj,
        api_key_hash=hashed_key,
    )

    session.add(new_client)
    await session.commit()
    await session.refresh(new_client)

    return {
        'id': new_client.id,
        'nome_instituicao': new_client.nome_instituicao,
        'cnpj': new_client.cnpj,
        'ativo': new_client.ativo,
        'data_criacao': new_client.data_criacao,
        'ultimo_acesso': new_client.ultimo_acesso,
        'api_key': plain_api_key,
    }


@router.get('/', response_model=list[schemas.ClientePublico])
async def list_instituicoes(session: T_Session, _: T_CurrentAdmin):
    result = await session.execute(select(Cliente))
    return result.scalars().all()


@router.get('/{id}', response_model=schemas.ClientePublico)
async def get_instituicao(id: str, session: T_Session, _: T_CurrentAdmin):
    cliente = await session.get(Cliente, id)
    if not cliente:
        raise HTTPException(
            status_code=404, detail='Instituição não encontrada'
        )
    return cliente


@router.patch('/{id}/status', response_model=schemas.ClientePublico)
async def alterar_status_instituicao(
    id: str, session: T_Session, _: T_CurrentAdmin
):
    cliente = await session.get(Cliente, id)
    if not cliente:
        raise HTTPException(
            status_code=404, detail='Instituição não encontrada'
        )

    cliente.ativo = not cliente.ativo
    await session.commit()
    await session.refresh(cliente)
    return cliente


@router.delete('/{id}', status_code=204)
async def delete_instituicao(id: str, session: T_Session, _: T_CurrentAdmin):
    cliente = await session.get(Cliente, id)
    if not cliente:
        raise HTTPException(
            status_code=404, detail='Instituição não encontrada'
        )

    await session.delete(cliente)
    await session.commit()
