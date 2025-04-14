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
        # Mostrar os primeiros valores da coluna 'Início da viagem' para diagnóstico
        st.subheader("Valores da coluna 'Início da viagem' (para diagnóstico)")
        st.write(df['Início da viagem'].head(20))  # Mostrar os 20 primeiros valores
        
        # Separar a coluna 'Início da viagem' em 'Data Início da viagem' e 'Hora Início da viagem'
        try:
            # Usando expressões regulares para extrair a data e a hora
            df['Data Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2} de \w{3}\. de \d{4})')[0]
            df['Hora Início da viagem'] = df['Início da viagem'].str.extract(r'(\d{2}:\d{2}:\d{2})')[0]
            
            # Converter a coluna 'Data Início da viagem' para o formato datetime
            df['Data Início da viagem'] = pd.to_datetime(df['Data Início da viagem'], format='%d de %b. de %Y', errors='coerce')

            # Converter a coluna 'Hora Início da viagem' para o formato hora
            df['Hora Início da viagem'] = pd.to_datetime(df['Hora Início da viagem'], format='%H:%M:%S', errors='coerce').dt.time

            # Verificar os valores que não puderam ser convertidos
            invalid_values = df[df['Data Início da viagem'].isnull() | df['Hora Início da viagem'].isnull()]

            if not invalid_values.empty:
                st.warning("Alguns valores na coluna 'Início da viagem' não puderam ser convertidos. Veja abaixo os valores problemáticos:")
                st.write(invalid_values)

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
