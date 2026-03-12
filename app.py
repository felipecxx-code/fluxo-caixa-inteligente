import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


st.title("Gestor de Fluxo de Caixa")
st.write("Sistema de controle financeiro.")

# Criar saldo na memória se não existir.
if "saldo" not in st.session_state:
    st.session_state.saldo = 0

if "transacoes" not in st.session_state:
    st.session_state.transacoes = []


st.sidebar.title("Menu")

tipo = st.sidebar.selectbox("Tipo de transação", ["Receita", "Despesa"])
if tipo == "Receita":
    categoria = st.sidebar.selectbox(
        "Categoria",
        ["Salário", "Outros"]
    )
else:
    categoria = st.sidebar.selectbox(
        "Categoria",
        ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"]
    )

valor = st.sidebar.number_input("Valor", min_value=0.00, step=0.01, format="%.2f")
valor = round(valor, 2)
btn_add = st.sidebar.button("Adicionar")
data = st.sidebar.date_input(
    "Data da transação",
    value=datetime.date.today(),
    format="DD/MM/YYYY"
)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}". replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_pdf(df):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    y = 750
    c.setFont("Helvetica", 10)

    for i, row in df.iterrows():
        linha = f"{row['Data']} | {row['Tipo']} | {row['Valor']}"
        c.drawString(50, y, linha)
        y -= 20

        if y < 50:  # nova página se acabar o espaço
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return buffer


# Ação botão
if btn_add: 
    nova_transacao = {
    "Data": data,        
    "Tipo": tipo,
    "Categoria": categoria,
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

    st.subheader("Exportar dados")

    col1, col2, col3 = st.columns(3)

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    with col1:
        st.download_button(
            label="📄 CSV",
            data=csv,
            file_name="transacoes.csv",
            mime="text/csv"
        )

    # Excel
    buffer_excel = io.BytesIO()
    df.to_excel(buffer_excel, index=False)
    with col2:
        st.download_button(
            label="📊 Excel",
            data=buffer_excel.getvalue(),
            file_name="transacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # PDF
    pdf = gerar_pdf(df)
    with col3:
        st.download_button(
            label="🧾 PDF",
            data=pdf,
            file_name="transacoes.pdf",
         mime="application/pdf"
        )

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

    st.subheader("Gastos por Categoria")
    df_despesas = df[df["Tipo"] == "Despesa"]
    gastos_categoria = df_despesas.groupby("Categoria")["Valor"].sum()
    st.bar_chart(gastos_categoria)


else:
    st.write("Nenhuma transação registrada ainda.")

