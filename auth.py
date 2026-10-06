from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from models import User


def criar_usuario(db: Session, nome: str, email: str, senha: str):
    usuario_existente = db.query(User).filter(User.email == email).first()

    if usuario_existente:
        return None

    novo_usuario = User(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha)
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(User).filter(User.email == email).first()

    if not usuario:
        return None

    if not check_password_hash(usuario.senha_hash, senha):
        return None

    return usuario