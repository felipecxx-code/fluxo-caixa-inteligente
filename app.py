import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime


st.title("FLUXO INTELIGENTE")
st.write("Sistema de controle financeiro.")

# Criar saldo na memória se não existir.
if "saldo" not in st.session_state:
    st.session_state.saldo = 0

if "transacoes" not in st.session_state:
    st.session_state.transacoes = []


st.sidebar.title("Menu")

tipo = st.sidebar.selectbox("Tipo de transação", ["Receita", "Despesa"])
valor = st.sidebar.number_input("Valor", min_value=0.0)
btn_add = st.sidebar.button("Adicionar")
data = st.sidebar.date_input(
    "Data da transação",
    value=datetime.date.today(),
    format="DD/MM/YYYY"
)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}". replace(",", "X").replace(".", ",").replace("X", ".")




# Ação botão
if btn_add: 
    nova_transacao = {
    "Data": data,        
    "Tipo": tipo,
    "Valor": valor
    }

    st.session_state.transacoes.append(nova_transacao)

    if tipo == "Receita":
        st.session_state.saldo += valor
    else:
        st.session_state.saldo -= valor
    


st.subheader("Histórico de Transações")
if st.session_state.transacoes:
    df = pd.DataFrame(st.session_state.transacoes)

    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df = df.sort_values(by="Data")

    df_exibir = df.copy()
    df_exibir["Data"] = df_exibir["Data"].dt.strftime("%d/%m/%Y")

    st.dataframe(df_exibir)

    total_receitas = df[df["Tipo"] == "Receita"] ["Valor"].sum()
    total_despesas = df[df["Tipo"] == "Despesa"] ["Valor"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Receitas: ", formatar_moeda(total_receitas))
    with col2:
        st.metric("Despesas:", formatar_moeda(total_despesas))
    with col3:
        st.metric("Saldo", formatar_moeda(st.session_state.saldo))
    

    dados_grafico = pd.DataFrame({
    "Tipo": ["Receita", "Despesa"],
    "Valor": [total_receitas, total_despesas]
    })

    st.subheader("Gráfico de Receitas vs Despesas")

    fig, ax = plt.subplots()

    tipos = ["Receita", "Despesa"]
    valores = [total_receitas, total_despesas]
    cores = ["green", "red"]

    barras = ax.bar(tipos, valores, color=cores)

    # Adiciona valores em cima das barras
    for barra in barras:
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            f'{altura:.2f}',
            ha='center',
            va='bottom'
        )

    ax.set_ylabel("Valor")
    ax.set_title("Receitas vs Despesas")

    st.pyplot(fig)

else:
    st.write("Nenhuma transação registrada ainda.")

