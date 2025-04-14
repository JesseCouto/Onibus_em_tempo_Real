import streamlit as st
import pandas as pd

# Título do aplicativo
st.title("Visualização de Dados CSV")

# Carregar arquivo CSV
st.sidebar.header("Carregar Dados CSV")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Ler os dados CSV
    df = pd.read_csv(uploaded_file)

    # Substituir "." por "," na coluna 'distância planejada' (ajustando para numeral brasileiro)
    if 'distância planejada' in df.columns:
        df['distância planejada'] = df['distância planejada'].astype(str).str.replace('.', ',', regex=False)

    # Exibir a tabela de dados brutos
    st.subheader("Dados Brutos")
    st.write(df)
