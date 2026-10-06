
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

st.sidebar.subheader(
    "Nova transação"
)

tipo = st.sidebar.selectbox(
    "Tipo de transação",
    [
        "Receita",
        "Despesa"
    ]
)


if tipo == "Receita":

    categoria = st.sidebar.selectbox(
        "Categoria",
        [
            "Salário",
            "Outros"
        ]
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


descricao = st.sidebar.text_input(
    "Descrição"
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
# SALVAR TRANSAÇÃO NO BANCO
# ============================================================

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
# HISTÓRICO
# ========================================================

    st.subheader(
        "📋 Histórico de Transações"
    )

    df_exibir = df.copy()

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
        df_exibir.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # GERENCIAR TRANSAÇÃO
    # ========================================================

    st.subheader(
        "✏️ Gerenciar Transação"
    )

    opcoes_transacoes = {}

    for transacao in transacoes:

        descricao = (
            transacao.descricao
            if transacao.descricao
            else "Sem descrição"
        )

        texto = (
            f"{transacao.data.strftime('%d/%m/%Y')} | "
            f"{transacao.tipo} | "
            f"{transacao.categoria} | "
            f"{descricao} | "
            f"{formatar_moeda(transacao.valor)}"
        )

        opcoes_transacoes[texto] = transacao.id


    transacao_selecionada = st.selectbox(
        "Selecione uma transação",
        list(opcoes_transacoes.keys())
    )


    id_selecionado = opcoes_transacoes[
        transacao_selecionada
    ]


    db = SessionLocal()

    transacao_atual = (
        db.query(Transacao)
        .filter(
            Transacao.id == id_selecionado,
            Transacao.usuario_id
            == st.session_state.usuario_id
        )
        .first()
    )

    db.close()


    if transacao_atual:

        with st.form(
            "form_editar_transacao"
        ):

            col1, col2 = st.columns(2)

            with col1:

                tipo_editado = st.selectbox(
                    "Tipo",
                    [
                        "Receita",
                        "Despesa"
                    ],
                    index=(
                        0
                        if transacao_atual.tipo == "Receita"
                        else 1
                    )
                )


            with col2:

                data_editada = st.date_input(
                    "Data",
                    value=transacao_atual.data.date(),
                    format="DD/MM/YYYY"
                )


            categorias_receita = [
                "Salário",
                "Outros"
            ]

            categorias_despesa = [
                "Alimentação",
                "Transporte",
                "Moradia",
                "Lazer",
                "Outros"
            ]


            if tipo_editado == "Receita":

                categorias = categorias_receita

            else:

                categorias = categorias_despesa


            categoria_atual = (
                transacao_atual.categoria
                if transacao_atual.categoria in categorias
                else categorias[0]
            )


            categoria_editada = st.selectbox(
                "Categoria",
                categorias,
                index=categorias.index(
                    categoria_atual
                )
            )


            descricao_editada = st.text_input(
                "Descrição",
                value=(
                    transacao_atual.descricao
                    or ""
                )
            )


            valor_editado = st.number_input(
                "Valor",
                min_value=0.00,
                step=0.01,
                format="%.2f",
                value=float(
                    transacao_atual.valor
                )
            )


            salvar_edicao = st.form_submit_button(
                "💾 Salvar alterações",
                use_container_width=True
            )


            if salvar_edicao:

                if valor_editado <= 0:

                    st.error(
                        "O valor deve ser maior que zero."
                    )

                elif not descricao_editada.strip():

                    st.error(
                        "Informe uma descrição."
                    )

                else:

                    db = SessionLocal()

                    editar_transacao(
                        db=db,
                        transacao_id=id_selecionado,
                        usuario_id=(
                            st.session_state.usuario_id
                        ),
                        data=datetime.datetime.combine(
                            data_editada,
                            datetime.time.min
                        ),
                        tipo=tipo_editado,
                        categoria=categoria_editada,
                        valor=valor_editado,
                        descricao=(
                            descricao_editada.strip()
                        )
                    )

                    db.close()

                    st.success(
                        "Transação atualizada com sucesso! ✏️"
                    )

                    st.rerun()

        # ====================================================
        # EXCLUIR TRANSAÇÃO
        # ====================================================

        st.divider()

        st.subheader(
            "🗑️ Excluir Transação"
        )

        st.warning(
            "Atenção: esta ação não poderá ser desfeita."
        )

        confirmar_exclusao = st.checkbox(
            "Sim, quero excluir esta transação."
        )

        if st.button(
            "🗑️ Excluir transação",
            use_container_width=True
        ):

            if not confirmar_exclusao:

                st.error(
                    "Marque a confirmação antes de excluir."
                )

            else:

                db = SessionLocal()

                sucesso = excluir_transacao(
                    db=db,
                    transacao_id=id_selecionado,
                    usuario_id=(
                        st.session_state.usuario_id
                    )
                )

                db.close()

                if sucesso:

                    st.success(
                        "Transação excluída com sucesso! 🗑️"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Não foi possível excluir a transação."
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
        total_receitas
        -
        total_despesas
    )


    st.divider()

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "💰 Receitas",
            formatar_moeda(
                total_receitas
            )
        )


    with col2:

        st.metric(
            "💸 Despesas",
            formatar_moeda(
                total_despesas
            )
        )


    with col3:

        st.metric(
            "📊 Saldo",
            formatar_moeda(
                saldo
            )
        )


    # ========================================================
    # EXPORTAÇÃO
    # ========================================================

    st.subheader(
        "📤 Exportar dados"
    )

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
    # GRÁFICO RECEITAS VS DESPESAS
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
            formatar_moeda(altura),
            ha="center",
            va="bottom"
        )

    ax.set_ylabel(
        "Valor"
    )

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

    if not df_despesas.empty:

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
            "Você ainda não possui despesas registradas."
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

