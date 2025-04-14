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

    # Verificar se a coluna 'Início da viagem' está presente
    if 'Início da viagem' in df.columns:
        # Mapeamento de meses para substituir a abreviação pelo número
        month_map = {
            'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
            'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
            'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
        }

        try:
            # Extrair a data no formato: "13 de jan. de 2025"
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            
            # Substituir as abreviações dos meses para o formato numérico
            df['Data Início da viagem'] = df['Data Início da viagem'].replace(month_map, regex=True)

            # Ajustar o formato da data para dd/mm/yyyy
            df['Data Início da viagem'] = df['Data Início da viagem'].str.replace(r' de ', '/', regex=True)

            # Converter para o formato datetime com o padrão dd/mm/yyyy
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d/%m/%Y', errors='coerce')

            # Remover a parte da hora da coluna 'Data Início da viagem'
            df['Data Início da viagem'] = df['Data Início da viagem'].dt.date

            # Extrair a hora da viagem
            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time

            # Limpar valores nulos da coluna 'Data Início da viagem' e 'Hora Início da viagem'
            df = df.dropna(subset=['Data Início da viagem', 'Hora Início da viagem'])

        except Exception as e:
            st.error(f"Erro ao separar e converter os dados: {e}")
        
        # Substituir "." por "," na coluna 'distancia_planejada' (ajustando para numeral brasileiro)
        if 'distancia_planejada' in df.columns:
            df['distancia_planejada'] = df['distancia_planejada'].astype(str).str.replace('.', ',', regex=False)

        # Exibir a tabela de dados brutos
        st.subheader("Dados Brutos")
        st.write(df)

    else:
        st.warning("A coluna 'Início da viagem' não foi encontrada no arquivo.")
