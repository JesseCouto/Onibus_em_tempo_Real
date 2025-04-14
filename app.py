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

    # Substituir "." por "," na coluna 'distancia_planejada' (ajustando para numeral brasileiro)
    if 'distancia_planejada' in df.columns:
        df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace('.', ',', regex=False)

    # Exibir a tabela de dados brutos
    st.subheader("Dados Brutos")
    st.write(df)

    # Verificar se a coluna 'Início de viagem' está no formato de hora
    if 'Início de viagem' in df.columns:
        # Converter 'Início de viagem' para datetime
        df['Início de viagem'] = pd.to_datetime(df['Início de viagem'], errors='coerce')

        # Criar as faixas horárias
        bins = ['00:00:00', '03:00:00', '06:00:00', '09:00:00', '12:00:00', '15:00:00', '18:00:00', '21:00:00', '23:59:59']
        labels = ['00:00-02:59', '03:00-05:59', '06:00-08:59', '09:00-11:59', '12:00-14:59', '15:00-17:59', '18:00-20:59', '21:00-23:59']

        # Adicionar a coluna 'Faixa Horária' com as faixas baseadas no 'Início de viagem'
        df['Faixa Horária'] = pd.cut(df['Início de viagem'].dt.hour, bins=[0, 2, 5, 8, 11, 14, 17, 20, 23], labels=labels, right=True)

        # Calcular a soma da distância planejada por 'Serviço' e 'Faixa Horária'
        df_grouped = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()

        # Exibir a tabela "Km Realizada por Faixa Horária" abaixo de "Dados Brutos"
        st.subheader("Km Realizada por Faixa Horária")
        st.write(df_grouped)
