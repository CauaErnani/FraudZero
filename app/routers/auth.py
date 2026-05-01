from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Cliente
from app.schemas import ClientePublico, Token
from app.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.settings import Settings

router = APIRouter(prefix='/auth', tags=['auth'])

T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[Cliente, Depends(get_current_user)]

settings = Settings()


@router.post('/login', response_model=Token)
async def login_for_access_token(
    form_data: T_OAuth2Form,
    session: T_Session,
):
    """
    Login para **Instituições Bancárias**.
    Use o **CNPJ** no campo `username` e a **API Key** no campo `password`.
    """
    cliente = await session.scalar(
        select(Cliente).where(Cliente.cnpj == form_data.username)
    )

    if not cliente or not verify_password(
        form_data.password, cliente.api_key_hash
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='CNPJ ou senha incorretos',
        )

    # Atualiza o último acesso
    cliente.ultimo_acesso = datetime.utcnow()
    await session.commit()

    access_token = create_access_token(
        data={'sub': cliente.cnpj, 'role': 'instituicao'}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/admin/login', response_model=Token)
async def admin_login(form_data: T_OAuth2Form):
    """
    Login para o **Administrador** do sistema.
    Use as credenciais definidas no `.env`.
    """
    if (
        form_data.username != settings.ADMIN_USERNAME
        or form_data.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Credenciais de administrador inválidas',
        )

    access_token = create_access_token(
        data={'sub': settings.ADMIN_USERNAME, 'role': 'admin'}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=ClientePublico)
async def read_users_me(current_user: T_CurrentUser):
    return current_user
