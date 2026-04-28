from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoTransacao(str, Enum):
    CASH_IN = 'CASH_IN'
    CASH_OUT = 'CASH_OUT'
    DEBIT = 'DEBIT'
    PAYMENT = 'PAYMENT'
    TRANSFER = 'TRANSFER'


class TransacaoEntrada(BaseModel):
    transaction_id: str
    user_id: str
    type: TipoTransacao
    amount: float = Field(..., gt=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrig: float = Field(..., ge=0)
    oldbalanceDest: float = Field(..., ge=0)
    newbalanceDest: float = Field(..., ge=0)


class PredicaoRisco(BaseModel):
    analysis_id: str
    is_fraud: bool
    risk_score: float


class LogAnalise(BaseModel):
    id_log: str
    timestamp: datetime
    dados_entrada: str
    predicao_retornada: str
    cliente_id: str


class ClienteBase(BaseModel):
    nome_instituicao: str
    cnpj: str = Field(..., min_length=14, max_length=14)

    @field_validator('cnpj')
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        # Apenas dígitos
        if not v.isdigit():
            raise ValueError('CNPJ deve conter apenas números')

        # Bloqueia sequências inválidas como 00000000000000
        if len(set(v)) == 1:
            raise ValueError('CNPJ inválido')

        # Validação dos dígitos verificadores
        def calc_digito(cnpj: str, pesos: list[int]) -> int:
            soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            RESTO_MINIMO = 2
            return 0 if resto < RESTO_MINIMO else 11 - resto

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        if calc_digito(v, pesos1) != int(v[12]):
            raise ValueError('CNPJ inválido')
        if calc_digito(v, pesos2) != int(v[13]):
            raise ValueError('CNPJ inválido')

        return v


class ClientePublico(ClienteBase):
    id: str
    ativo: bool
    data_criacao: datetime
    ultimo_acesso: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ClienteSchema(ClienteBase):
    pass


class ClienteCreateResponse(ClientePublico):
    api_key: str


class Token(BaseModel):
    access_token: str
    token_type: str
