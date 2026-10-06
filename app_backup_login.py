import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from database import SessionLocal
from auth import criar_usuario, autenticar_usuario


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Fluxo Caixa Inteligente",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================

def tela_login():
    st.title("💰 Fluxo Caixa Inteligente")
    st.subheader("Acesse sua conta")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):
        if not email or not senha:
            st.warning("Preencha e-mail e senha.")
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

            st.success("Login realizado com sucesso!")

            st.rerun()

        else:
            st.error("E-mail ou senha incorretos.")

    st.divider()

    st.write("Ainda não possui uma conta?")

    if st.button("Criar minha conta", use_container_width=True):
        st.session_state.tela = "cadastro"
        st.rerun()


def tela_cadastro():
    st.title("💰 Fluxo Caixa Inteligente")
    st.subheader("Criar sua conta")

    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar_senha = st.text_input(
        "Confirmar senha",
        type="password"
    )

    if st.button("Cadastrar", use_container_width=True):

        if not nome or not email or not senha:
            st.warning("Preencha todos os campos.")
            return

        if senha != confirmar_senha:
            st.error("As senhas não são iguais.")
            return

        if len(senha) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
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

    if st.button("Voltar para o login", use_container_width=True):
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

st.title("💰 Gestor de Fluxo de Caixa")

st.write(
    f"Olá, **{st.session_state.usuario_nome}**! 👋"
)

# Inicialização temporária das transações
# Ainda vamos ligar isso ao banco na próxima etapa.

if "saldo" not in st.session_state:
    st.session_state.saldo = 0

if "transacoes" not in st.session_state:
    st.session_state.transacoes = []


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Menu")

st.sidebar.write(
    f"👤 {st.session_state.usuario_nome}"
)

st.sidebar.divider()

tipo = st.sidebar.selectbox(
    "Tipo de transação",
    ["Receita", "Despesa"]
)

if tipo == "Receita":

    categoria = st.sidebar.selectbox(
        "Categoria",
        ["Salário", "Outros"]
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
        ]
    )

valor = st.sidebar.number_input(
    "Valor",
    min_value=0.00,
    step=0.01,
    format="%.2f"
)

data = st.sidebar.date_input(
    "Data da transação",
    value=datetime.date.today(),
    format="DD/MM/YYYY"
)

btn_add = st.sidebar.button(
    "Adicionar",
    use_container_width=True
)


# ============================================================
# ADICIONAR TRANSAÇÃO
# ============================================================

if btn_add:

    if valor <= 0:

        st.sidebar.warning(
            "Informe um valor maior que zero."
        )

    else:

        nova_transacao = {
            "Data": data,
            "Tipo": tipo,
            "Categoria": categoria,
            "Valor": valor
        }

        st.session_state.transacoes.append(
            nova_transacao
        )

        if tipo == "Receita":
            st.session_state.saldo += valor

        else:
            st.session_state.saldo -= valor

        st.success(
            "Transação adicionada com sucesso!"
        )


# ============================================================
# HISTÓRICO
# ============================================================

st.subheader("Histórico de Transações")

if st.session_state.transacoes:

    df = pd.DataFrame(
        st.session_state.transacoes
    )

    df["Data"] = pd.to_datetime(
        df["Data"]
    )

    df = df.sort_values(
        by="Data"
    )

    df_exibir = df.copy()

    df_exibir["Data"] = (
        df_exibir["Data"]
        .dt.strftime("%d/%m/%Y")
    )

    st.dataframe(
        df_exibir,
        use_container_width=True
    )


    # ========================================================
    # EXPORTAÇÃO
    # ========================================================

    st.subheader("Exportar dados")

    col1, col2, col3 = st.columns(3)


    # CSV
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


    # Excel
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


    # PDF
    pdf = gerar_pdf(df)

    with col3:

        st.download_button(
            label="📑 PDF",
            data=pdf,
            file_name="transacoes.pdf",
            mime="application/pdf",
            use_container_width=True
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

    saldo = (
        total_receitas -
        total_despesas
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Receitas",
            formatar_moeda(
                total_receitas
            )
        )

    with col2:

        st.metric(
            "Despesas",
            formatar_moeda(
                total_despesas
            )
        )

    with col3:

        st.metric(
            "Saldo",
            formatar_moeda(
                saldo
            )
        )


    # ========================================================
    # GRÁFICO
    # ========================================================

    st.subheader(
        "📊 Receitas vs Despesas"
    )

    fig, ax = plt.subplots()

    tipos = [
        "Receita",
        "Despesa"
    ]

    valores = [
        total_receitas,
        total_despesas
    ]

    cores = [
        "green",
        "red"
    ]

    barras = ax.bar(
        tipos,
        valores,
        color=cores
    )

    for barra in barras:

        altura = barra.get_height()

        ax.text(
            barra.get_x()
            + barra.get_width() / 2,
            altura,
            f"{altura:.2f}",
            ha="center",
            va="bottom"
        )

    ax.set_ylabel("Valor")

    ax.set_title(
        "Receitas vs Despesas"
    )

    st.pyplot(fig)


    # ========================================================
    # GASTOS POR CATEGORIA
    # ========================================================

    st.subheader(
        "💸 Gastos por Categoria"
    )

    df_despesas = df[
        df["Tipo"] == "Despesa"
    ]

    gastos_categoria = (
        df_despesas
        .groupby("Categoria")["Valor"]
        .sum()
    )

    st.bar_chart(
        gastos_categoria
    )


else:

    st.info(
        "Nenhuma transação registrada ainda."
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

