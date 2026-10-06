
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from database import SessionLocal
from models import Transacao
from auth import criar_usuario, autenticar_usuario
from transacoes import (
    adicionar_transacao,
    buscar_transacoes,
    editar_transacao,
    excluir_transacao
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Fluxo Caixa Inteligente",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown(
    """
    <style>

    /* Área principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Títulos */
    h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        font-weight: 600;
    }

    /* Cards financeiros */
    .card-financeiro {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        min-height: 120px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .card-titulo {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 8px;
    }

    .card-valor {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
    }

    /* Tabela */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Botões */
    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
) 


# ============================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================

def tela_login():

    st.title("💰 Fluxo Caixa Inteligente")
    st.subheader("Acesse sua conta")

    email = st.text_input("E-mail")
    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button(
        "Entrar",
        use_container_width=True
    ):

        if not email or not senha:
            st.warning(
                "Preencha e-mail e senha."
            )
            return

        db = SessionLocal()

        usuario = autenticar_usuario(
            db,
            email,
            senha
        )

        db.close()

        if usuario:

            st.session_state.logado = True
            st.session_state.usuario_id = usuario.id
            st.session_state.usuario_nome = usuario.nome
            st.session_state.usuario_email = usuario.email

            st.success(
                "Login realizado com sucesso!"
            )

            st.rerun()

        else:

            st.error(
                "E-mail ou senha incorretos."
            )

    st.divider()

    st.write(
        "Ainda não possui uma conta?"
    )

    if st.button(
        "Criar minha conta",
        use_container_width=True
    ):

        st.session_state.tela = "cadastro"

        st.rerun()


def tela_cadastro():

    st.title("💰 Fluxo Caixa Inteligente")
    st.subheader("Criar sua conta")

    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input(
        "Senha",
        type="password"
    )

    confirmar_senha = st.text_input(
        "Confirmar senha",
        type="password"
    )

    if st.button(
        "Cadastrar",
        use_container_width=True
    ):

        if not nome or not email or not senha:

            st.warning(
                "Preencha todos os campos."
            )

            return

        if senha != confirmar_senha:

            st.error(
                "As senhas não são iguais."
            )

            return

        if len(senha) < 6:

            st.error(
                "A senha deve ter pelo menos 6 caracteres."
            )

            return

        db = SessionLocal()

        usuario = criar_usuario(
            db,
            nome,
            email,
            senha
        )

        db.close()

        if usuario:

            st.success(
                "Conta criada com sucesso! "
                "Agora você pode fazer login."
            )

            st.session_state.tela = "login"

            st.rerun()

        else:

            st.error(
                "Este e-mail já está cadastrado."
            )

    st.divider()

    if st.button(
        "Voltar para o login",
        use_container_width=True
    ):

        st.session_state.tela = "login"

        st.rerun()


# ============================================================
# FUNÇÕES DO SISTEMA FINANCEIRO
# ============================================================

def formatar_moeda(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def gerar_pdf(df):

    buffer = io.BytesIO()

    c = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    y = 750

    c.setFont(
        "Helvetica",
        10
    )

    for _, row in df.iterrows():

        linha = (
            f"{row['Data']} | "
            f"{row['Tipo']} | "
            f"{row['Categoria']} | "
            f"{row['Descricao']} | "
            f"R$ {row['Valor']:.2f}"
        )

        c.drawString(
            50,
            y,
            linha
        )

        y -= 20

        if y < 50:

            c.showPage()

            y = 750

    c.save()

    buffer.seek(0)

    return buffer


# ============================================================
# ESTADO DA SESSÃO
# ============================================================

if "logado" not in st.session_state:

    st.session_state.logado = False


if "tela" not in st.session_state:

    st.session_state.tela = "login"


if "mostrar_nova_transacao" not in st.session_state:

    st.session_state.mostrar_nova_transacao = False


if "mostrar_gerenciar" not in st.session_state:

    st.session_state.mostrar_gerenciar = False


if "confirmar_exclusao" not in st.session_state:

    st.session_state.confirmar_exclusao = False


# ============================================================
# CONTROLE DE ACESSO
# ============================================================

if not st.session_state.logado:

    if st.session_state.tela == "cadastro":

        tela_cadastro()

    else:

        tela_login()

    st.stop()


# ============================================================
# SISTEMA PRINCIPAL
# ============================================================

st.title(
    "💰 Gestor de Fluxo de Caixa"
)

st.write(
    f"Olá, **{st.session_state.usuario_nome}**! 👋"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Menu")

st.sidebar.write(
    f"👤 {st.session_state.usuario_nome}"
)

st.sidebar.write(
    st.session_state.usuario_email
)

st.sidebar.divider()


# ============================================================
# NOVA TRANSAÇÃO
# ============================================================

if "mostrar_nova_transacao" not in st.session_state:

    st.session_state.mostrar_nova_transacao = False


if st.sidebar.button(
    "➕ Nova transação",
    use_container_width=True
):

    st.session_state.mostrar_nova_transacao = True
    st.session_state.mostrar_gerenciar = False
    st.session_state.confirmar_exclusao = False

    st.rerun()


# ============================================================
# FORMULÁRIO DE NOVA TRANSAÇÃO
# ============================================================

if st.session_state.mostrar_nova_transacao:

    st.sidebar.divider()

    st.sidebar.subheader(
        "➕ Nova transação"
    )

    tipo = st.sidebar.selectbox(
        "Tipo de transação",
        [
            "Receita",
            "Despesa"
        ],
        key="nova_tipo"
    )


    if tipo == "Receita":

        categoria = st.sidebar.selectbox(
            "Categoria",
            [
                "Salário",
                "Outros"
            ],
            key="nova_categoria_receita"
        )

    else:

        categoria = st.sidebar.selectbox(
            "Categoria",
            [
                "Alimentação",
                "Transporte",
                "Moradia",
                "Lazer",
                "Outros"
            ],
            key="nova_categoria_despesa"
        )


    descricao = st.sidebar.text_input(
        "Descrição",
        key="nova_descricao"
    )


    valor = st.sidebar.number_input(
        "Valor",
        min_value=0.00,
        step=0.01,
        format="%.2f",
        key="nova_valor"
    )


    data = st.sidebar.date_input(
        "Data da transação",
        value=datetime.date.today(),
        format="DD/MM/YYYY",
        key="nova_data"
    )


    col_salvar, col_cancelar = st.sidebar.columns(2)


    with col_salvar:

        btn_add = st.button(
            "💾 Adicionar",
            use_container_width=True,
            key="btn_adicionar_transacao"
        )


    with col_cancelar:

        btn_cancelar = st.button(
            "❌ Cancelar",
            use_container_width=True,
            key="btn_cancelar_nova_transacao"
        )


    # ========================================================
    # CANCELAR
    # ========================================================

    if btn_cancelar:

        st.session_state.mostrar_nova_transacao = False

        st.rerun()


    # ========================================================
    # SALVAR
    # ========================================================

    if btn_add:

        if valor <= 0:

            st.sidebar.warning(
                "Informe um valor maior que zero."
            )

        elif not descricao.strip():

            st.sidebar.warning(
                "Informe uma descrição."
            )

        else:

            db = SessionLocal()

            adicionar_transacao(
                db=db,
                usuario_id=st.session_state.usuario_id,
                data=datetime.datetime.combine(
                    data,
                    datetime.time.min
                ),
                tipo=tipo,
                categoria=categoria,
                valor=valor,
                descricao=descricao.strip()
            )

            db.close()

            st.session_state.mostrar_nova_transacao = False

            st.success(
                "Transação salva com sucesso! 💾"
            )

            st.rerun()


# ============================================================
# BUSCAR TRANSAÇÕES DO USUÁRIO
# ============================================================

db = SessionLocal()

transacoes = buscar_transacoes(
    db,
    st.session_state.usuario_id
)

db.close()


# ============================================================
# TRANSFORMA BANCO EM DATAFRAME
# ============================================================

if transacoes:

    dados = []

    for transacao in transacoes:

        dados.append(
            {
                "ID": transacao.id,
                "Data": transacao.data,
                "Tipo": transacao.tipo,
                "Categoria": transacao.categoria,
                "Descricao": transacao.descricao or "",
                "Valor": transacao.valor
            }
        )

    df = pd.DataFrame(dados)

    df["Data"] = pd.to_datetime(
        df["Data"]
    )

    df = df.sort_values(
        by="Data",
        ascending=False
    )


# ========================================================
# INDICADORES
# ========================================================

total_receitas = df[
    df["Tipo"] == "Receita"
]["Valor"].sum()

total_despesas = df[
    df["Tipo"] == "Despesa"
]["Valor"].sum()

saldo = total_receitas - total_despesas


st.divider()

st.subheader("📊 Resumo financeiro")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="card-financeiro">
            <div class="card-titulo">💰 RECEITAS</div>
            <div class="card-valor">
                {formatar_moeda(total_receitas)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="card-financeiro">
            <div class="card-titulo">💸 DESPESAS</div>
            <div class="card-valor">
                {formatar_moeda(total_despesas)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="card-financeiro">
            <div class="card-titulo">📊 SALDO</div>
            <div class="card-valor">
                {formatar_moeda(saldo)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ========================================================
# FILTROS
# ========================================================

col_busca, col_tipo, col_categoria = st.columns([2, 1, 1])

with col_busca:

    busca = st.text_input(
        "🔎 Buscar",
        placeholder="Descrição ou categoria..."
    )

with col_tipo:

    filtro_tipo = st.selectbox(
        "Tipo",
        [
            "Todos",
            "Receita",
            "Despesa"
        ]
    )

with col_categoria:

    categorias_disponiveis = [
        "Todas"
    ] + sorted(
        df["Categoria"].dropna().unique().tolist()
    )

    filtro_categoria = st.selectbox(
        "Categoria",
        categorias_disponiveis
    )


# ========================================================
# APLICAR FILTROS
# ========================================================

df_filtrado = df.copy()

if busca:

    busca = busca.lower().strip()

    df_filtrado = df_filtrado[
        df_filtrado["Descricao"]
        .str.lower()
        .str.contains(
            busca,
            na=False
        )
        |
        df_filtrado["Categoria"]
        .str.lower()
        .str.contains(
            busca,
            na=False
        )
    ]


if filtro_tipo != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Tipo"] == filtro_tipo
    ]


if filtro_categoria != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Categoria"] == filtro_categoria
    ]



# ========================================================
# BOTÃO GERENCIAR
# ========================================================

col_titulo, col_gerenciar = st.columns([4, 1])

with col_titulo:

    st.subheader(
        "📋 Histórico de Transações"
    )

with col_gerenciar:

    if st.button(
        "✏️ Gerenciar",
        use_container_width=True
    ):

        st.session_state.mostrar_gerenciar = True
        st.session_state.mostrar_nova_transacao = False
        st.session_state.confirmar_exclusao = False

        st.rerun()


# ========================================================
# GERENCIAR TRANSAÇÃO
# ========================================================

if st.session_state.mostrar_gerenciar:

    st.sidebar.divider()

    st.sidebar.subheader(
        "✏️ Gerenciar transação"
    )

    opcoes_transacoes = {}

    for _, linha in df.iterrows():

        descricao_transacao = linha["Descricao"]

        if not descricao_transacao:

            descricao_transacao = "Sem descrição"

        texto = (
            f'{linha["Data"].strftime("%d/%m/%Y")} - '
            f'{descricao_transacao} - '
            f'{formatar_moeda(linha["Valor"])}'
        )

        opcoes_transacoes[texto] = linha["ID"]


    transacao_selecionada = st.sidebar.selectbox(
        "Selecione uma transação",
        list(opcoes_transacoes.keys())
    )


    transacao_id = opcoes_transacoes[
        transacao_selecionada
    ]


    transacao_atual = df[
        df["ID"] == transacao_id
    ].iloc[0]


    st.sidebar.divider()


    # ====================================================
    # CAMPOS
    # ====================================================

    nova_data = st.sidebar.date_input(
        "Data",
        value=transacao_atual["Data"].date(),
        format="DD/MM/YYYY",
        key="editar_data"
    )


    novo_tipo = st.sidebar.selectbox(
        "Tipo",
        [
            "Receita",
            "Despesa"
        ],
        index=(
            0
            if transacao_atual["Tipo"] == "Receita"
            else 1
        ),
        key="editar_tipo"
    )


    if novo_tipo == "Receita":

        categorias_edicao = [
            "Salário",
            "Outros"
        ]

    else:

        categorias_edicao = [
            "Alimentação",
            "Transporte",
            "Moradia",
            "Lazer",
            "Outros"
        ]


    categoria_atual = transacao_atual["Categoria"]

    if categoria_atual not in categorias_edicao:

        categorias_edicao.append(
            categoria_atual
        )


    nova_categoria = st.sidebar.selectbox(
        "Categoria",
        categorias_edicao,
        index=categorias_edicao.index(
            categoria_atual
        ),
        key="editar_categoria"
    )


    nova_descricao = st.sidebar.text_input(
        "Descrição",
        value=transacao_atual["Descricao"],
        key="editar_descricao"
    )


    novo_valor = st.sidebar.number_input(
        "Valor",
        min_value=0.00,
        value=float(transacao_atual["Valor"]),
        step=0.01,
        format="%.2f",
        key="editar_valor"
    )


    st.sidebar.divider()


    col_salvar, col_excluir = st.sidebar.columns(2)


    with col_salvar:

        btn_salvar_edicao = st.button(
            "💾 Salvar",
            use_container_width=True,
            key="btn_salvar_edicao"
        )


    with col_excluir:

        btn_excluir = st.button(
            "🗑️ Excluir",
            use_container_width=True,
            key="btn_excluir_transacao"
        )


    btn_cancelar_edicao = st.sidebar.button(
        "❌ Cancelar",
        use_container_width=True,
        key="btn_cancelar_edicao"
    )


    # ====================================================
    # CANCELAR
    # ====================================================

    if btn_cancelar_edicao:

        st.session_state.mostrar_gerenciar = False

        st.rerun()


    # ====================================================
    # SALVAR ALTERAÇÃO
    # ====================================================

    if btn_salvar_edicao:

        if novo_valor <= 0:

            st.sidebar.error(
                "O valor deve ser maior que zero."
            )

        elif not nova_descricao.strip():

            st.sidebar.error(
                "Informe uma descrição."
            )

        else:

            db = SessionLocal()

            editar_transacao(
                db=db,
                transacao_id=transacao_id,
                usuario_id=st.session_state.usuario_id,
                data=datetime.datetime.combine(
                    nova_data,
                    datetime.time.min
                ),
                tipo=novo_tipo,
                categoria=nova_categoria,
                valor=novo_valor,
                descricao=nova_descricao.strip()
            )

            db.close()

            st.session_state.mostrar_gerenciar = False

            st.success(
                "Transação atualizada com sucesso! 💾"
            )

            st.rerun()


    # ====================================================
    # EXCLUIR
    # ====================================================

    if btn_excluir:

        st.session_state.confirmar_exclusao = True

        st.rerun()


# ========================================================
# CONFIRMAÇÃO DE EXCLUSÃO
# ========================================================

if st.session_state.get(
    "confirmar_exclusao",
    False
):

    st.sidebar.warning(
        "⚠️ Tem certeza que deseja excluir esta transação?"
    )


    col_sim, col_nao = st.sidebar.columns(2)


    with col_sim:

        confirmar = st.button(
            "Sim, excluir",
            use_container_width=True,
            key="btn_confirmar_exclusao"
        )


    with col_nao:

        cancelar_exclusao = st.button(
            "Cancelar",
            use_container_width=True,
            key="btn_cancelar_exclusao"
        )


    if cancelar_exclusao:

        st.session_state.confirmar_exclusao = False

        st.rerun()


    if confirmar:

        db = SessionLocal()

        excluir_transacao(
            db=db,
            transacao_id=transacao_id,
            usuario_id=st.session_state.usuario_id
        )

        db.close()

        st.session_state.confirmar_exclusao = False
        st.session_state.mostrar_gerenciar = False

        st.success(
            "Transação excluída com sucesso! 🗑️"
        )

        st.rerun()


# ========================================================
# TABELA
# ========================================================

if not df_filtrado.empty:

    df_exibir = df_filtrado.copy()

    df_exibir["Data"] = (
        df_exibir["Data"]
        .dt.strftime("%d/%m/%Y")
    )

    df_exibir["Valor"] = (
        df_exibir["Valor"]
        .apply(formatar_moeda)
    )

    df_exibir = df_exibir[
        [
            "ID",
            "Data",
            "Tipo",
            "Categoria",
            "Descricao",
            "Valor"
        ]
    ]

    st.dataframe(
        df_exibir.drop(
            columns=["ID"]
        ),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"{len(df_filtrado)} "
        f"transação(ões) encontrada(s)."
    )

else:

    st.info(
        "Nenhuma transação encontrada "
        "com os filtros selecionados."
    )


# ========================================================
# EXPORTAÇÃO
# ========================================================

st.subheader("📤 Exportar dados")

col1, col2, col3 = st.columns(3)

csv = df.to_csv(
    index=False
).encode("utf-8")

with col1:

    st.download_button(
        label="📄 CSV",
        data=csv,
        file_name="transacoes.csv",
        mime="text/csv",
        use_container_width=True
    )


buffer_excel = io.BytesIO()

df.to_excel(
    buffer_excel,
    index=False
)

with col2:

    st.download_button(
        label="📊 Excel",
        data=buffer_excel.getvalue(),
        file_name="transacoes.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )


pdf = gerar_pdf(df)

with col3:

    st.download_button(
        label="📑 PDF",
        data=pdf,
        file_name="transacoes.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ============================================================
# LOGOUT
# ============================================================

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Sair",
    use_container_width=True
):

    st.session_state.clear()

    st.rerun()

