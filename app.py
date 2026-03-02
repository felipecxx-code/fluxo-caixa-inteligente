import streamlit as st


st.title("FLUXO INTELIGENTE")
st.write("Sistema de controle financeiro.")

# Criar saldo na memória se não existir.
if "saldo" not in st.session_state:
    st.session_state.saldo = 0


st.sidebar.title("Menu")

tipo = st.sidebar.selectbox("Tipo de transação", ["Receita", "Despesa"])
valor = st.sidebar.number_input("Valor", min_value=0.0)
btn_add = st.sidebar.button("Adicionar")

# Ação botão
if btn_add: 
    if tipo == "Receita":
        st.session_state.saldo += valor
    else:
        st.session_state.saldo -= valor
    

st.write("Saldo:", st.session_state.saldo)
