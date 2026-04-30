import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


@mapped_as_dataclass(table_registry)
class Cliente:
    __tablename__ = 'clientes'

    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4()), init=False
    )
    nome_instituicao: Mapped[str] = mapped_column(unique=True, nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)
    data_criacao: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    ultimo_acesso: Mapped[datetime] = mapped_column(
        init=False, default=func.now(), onupdate=func.now()
    )

    logs: Mapped[list['LogAnalise']] = relationship(
        'LogAnalise',
        back_populates='cliente',
        init=False,
        cascade='all, delete-orphan',
    )


@mapped_as_dataclass(table_registry)
class LogAnalise:
    __tablename__ = 'logs_analise'

    id_log: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4()), init=False
    )
    dados_entrada: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(init=False, default=func.now())
    predicao_retornada: Mapped[str] = mapped_column(nullable=False)

    cliente_id: Mapped[str] = mapped_column(
        ForeignKey('clientes.id'), nullable=False
    )

    cliente: Mapped['Cliente'] = relationship(
        'Cliente', back_populates='logs', init=False
    )
