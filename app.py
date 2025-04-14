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

    # Verificar e processar a coluna 'Início da viagem'
    if 'Início da viagem' in df.columns:
        # Tentar converter a coluna 'Início da viagem' para datetime, com erro 'coerce' para valores inválidos
        df['Início da viagem'] = pd.to_datetime(df['Início da viagem'], errors='coerce', format='%H:%M:%S')

        # Verifique se a conversão foi bem-sucedida
        if df['Início da viagem'].isnull().any():
            st.warning("Alguns valores na coluna 'Início da viagem' não puderam ser convertidos para data/hora. Estes registros foram removidos.")

        # Limpar valores nulos da coluna 'Início da viagem'
        df = df.dropna(subset=['Início da viagem'])

        # Garantir que 'Início da viagem' está no formato correto de hora
        df['Hora'] = df['Início da viagem'].dt.hour

        # Criar as faixas horárias
        bins = [0, 2, 5, 8, 11, 14, 17, 20, 23, 24]  # Intervalos de hora
        labels = ['00:00-02:59', '03:00-05:59', '06:00-08:59', '09:00-11:59', '12:00-14:59', '15:00-17:59', '18:00-20:59', '21:00-23:59']
        
        # Adicionar a coluna 'Faixa Horária' com as faixas baseadas no 'Hora'
        df['Faixa Horária'] = pd.cut(df['Hora'], bins=bins, labels=labels, right=False)

        # Calcular a soma da distância planejada por 'Serviço' e 'Faixa Horária'
        df_grouped = df.groupby(['Serviço', 'Faixa Horária'])['distancia_planejada'].sum().reset_index()

        # Exibir a tabela "Km Realizada por Faixa Horária" abaixo de "Dados Brutos"
        st.subheader("Km Realizada por Faixa Horária")
        st.write(df_grouped)
    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo.")
