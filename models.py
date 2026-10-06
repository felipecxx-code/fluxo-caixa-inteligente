from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    data = Column(
        DateTime,
        nullable=False
    )

    tipo = Column(
        String(20),
        nullable=False
    )

    categoria = Column(
        String(100),
        nullable=False
    )

    valor = Column(
        Float,
        nullable=False
    )

    descricao = Column(
        String(255),
        nullable=True
    )

    data_criacao = Column(
        DateTime,
        default=datetime.utcnow
    )

