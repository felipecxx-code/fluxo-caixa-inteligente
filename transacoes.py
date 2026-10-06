
from sqlalchemy.orm import Session

from models import Transacao


def adicionar_transacao(
    db: Session,
    usuario_id: int,
    data,
    tipo: str,
    categoria: str,
    valor: float,
    descricao: str = ""
):
    nova_transacao = Transacao(
        usuario_id=usuario_id,
        data=data,
        tipo=tipo,
        categoria=categoria,
        valor=valor,
        descricao=descricao
    )

    db.add(nova_transacao)
    db.commit()
    db.refresh(nova_transacao)

    return nova_transacao


def buscar_transacoes(
    db: Session,
    usuario_id: int
):
    return (
        db.query(Transacao)
        .filter(
            Transacao.usuario_id == usuario_id
        )
        .order_by(
            Transacao.data.desc()
        )
        .all()
    )


def buscar_transacao(
    db: Session,
    transacao_id: int,
    usuario_id: int
):
    return (
        db.query(Transacao)
        .filter(
            Transacao.id == transacao_id,
            Transacao.usuario_id == usuario_id
        )
        .first()
    )


def editar_transacao(
    db: Session,
    transacao_id: int,
    usuario_id: int,
    data,
    tipo: str,
    categoria: str,
    valor: float,
    descricao: str = ""
):
    transacao = buscar_transacao(
        db,
        transacao_id,
        usuario_id
    )

    if not transacao:
        return None

    transacao.data = data
    transacao.tipo = tipo
    transacao.categoria = categoria
    transacao.valor = valor
    transacao.descricao = descricao

    db.commit()
    db.refresh(transacao)

    return transacao


def excluir_transacao(
    db: Session,
    transacao_id: int,
    usuario_id: int
):
    transacao = buscar_transacao(
        db,
        transacao_id,
        usuario_id
    )

    if not transacao:
        return False

    db.delete(transacao)
    db.commit()

    return True

