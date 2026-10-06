from flask import Flask, request
from transacoes import adicionar_transacao
from database import SessionLocal
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def inicio():
    return "API Funcionando!"

@app.route("/teste")
def teste():
    return {
        "mensagem": "GET Funcionando!",
        "projeto": "Fluxo caixa inteligente"
        }

@app.route("/teste-post", methods=["post"])
def teste_post():
    return {
        "mensagem": "POST Funcionando!"
        }



@app.route("/teste-post2", methods=["post"])
def teste_post2():
    dados = request.json
    return dados

@app.route("/categoria", methods=["post"])
def categoria():
    dados = request.json
    return {
        "mensagem": "Categoria recebida",
        "categoria": dados["nome"]
        
    } 

@app.route("/transacao", methods=["post"])
def transacao():
    dados = request.json
    db = SessionLocal()
    usuario_id = 1
    data = datetime.now()
    create_transicion = adicionar_transacao(db,
        usuario_id,
        data,
        dados["tipo"],
        dados["categoria"],
        dados["valor"]
    )
    return {
        "mensagem": "Transação criada com sucesso",
        "usuario_id": create_transicion.usuario_id,
        "data": create_transicion.data.isoformat(),
        "tipo": create_transicion.tipo,
        "categoria": create_transicion.categoria,
        "valor": create_transicion.valor
        }
    