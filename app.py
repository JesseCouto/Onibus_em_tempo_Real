import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Título do aplicativo
st.title("Análise de Dados CSV")

# Carregar arquivo CSV
st.sidebar.header("Carregar Dados CSV")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Ler os dados CSV
    df = pd.read_csv(uploaded_file)

    # Exibir a tabela de dados
    st.subheader("Tabela de Dados")
    st.write(df)

    # Exibir uma descrição do DataFrame
    st.subheader("Resumo dos Dados")
    st.write(df.describe())

    # Opção para escolher a coluna para o gráfico
    st.sidebar.subheader("Escolher coluna para visualização")
    columns = df.select_dtypes(include=['number']).columns.tolist()
    selected_column = st.sidebar.selectbox("Escolha uma coluna", columns)

    # Exibir gráfico de barras ou histograma
    st.subheader(f"Distribuição da Coluna: {selected_column}")
    fig, ax = plt.subplots()
    sns.histplot(df[selected_column], kde=True, ax=ax)
    st.pyplot(fig)

    # Gráfico de dispersão entre duas colunas
    st.sidebar.subheader("Gráfico de Dispersão")
    x_column = st.sidebar.selectbox("Escolha a coluna X", columns)
    y_column = st.sidebar.selectbox("Escolha a coluna Y", columns)
    
    st.subheader(f"Gráfico de Dispersão entre {x_column} e {y_column}")
    fig, ax = plt.subplots()
    sns.scatterplot(x=df[x_column], y=df[y_column], ax=ax)
    st.pyplot(fig)

    # Gráfico de linha (opcional)
    st.subheader(f"Gráfico de Linha de {selected_column}")
    fig, ax = plt.subplots()
    df[selected_column].plot(kind="line", ax=ax)
    st.pyplot(fig)

    # Estatísticas adicionais
    st.subheader("Correlação entre as Colunas")
    st.write(df.corr())
